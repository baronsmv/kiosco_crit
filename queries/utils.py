import inspect
import json
from dataclasses import asdict
from datetime import date
from typing import Callable, Dict, List, Optional, Tuple, Type, Union

import requests
from django.conf import settings
from django.db import connections, OperationalError
from django.forms import Form
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from classes.contexts import ContextList
from classes.exceptions import AjaxException
from classes.models import BaseModel
from classes.selections import SelectionList
from utils import get
from utils.decorators import ajax_handler
from utils.logger import get_logger
from .models import Consulta

logger = get_logger(__name__)
base_url = settings.WHATSAPP_API_BASE_URL


def whatsapp_status(url: str = f"{base_url}/status") -> Dict:
    try:
        return requests.get(url).json()
    except Exception:
        return {"status": "desconocido", "connected": False}


def initial_context(context: Dict) -> Dict:
    return {
        **context,
        "whatsapp_status": whatsapp_status(),
        "id": "",
        "sujeto": None,
        "tabla": (),
        "id_proporcionado": False,
        "id_error": False,
        "date_error": False,
        "mensaje_ajax": "",
        "error_target": "",
    }


def evaluate_query(query: Callable, params: Dict) -> Tuple[str, Tuple[str, ...]]:
    sig = inspect.signature(query)
    return query(**{k: v for k, v in params.items() if k in sig.parameters})


def get_rows(
    query_func: Callable,
    query_params: Dict,
    db_name: str = "crit",
):
    query, params = evaluate_query(query_func, query_params)
    logger.debug(f"Ejecutando consulta: '{query}', con parámetros: '{params}'.")

    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute(query, params)
            columnas = tuple(col[0] for col in cursor.description)
            return [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except OperationalError as e:
        logger.error(f"No se pudo conectar con la base de datos: {e}")
        raise AjaxException("❌ No se pudo conectar con la base de datos.")
    except Exception as e:
        logger.exception(f"Error al obtener objetos: {str(e)}")
        raise AjaxException()


def get_objects(
    rows: List[Dict],
    selection_list: SelectionList,
    nombre_id: str,
    nombre_sujeto: str,
    nombre_objetos: str,
) -> Optional[Dict]:

    sujeto = None
    objetos = []

    if selection_list.subject:
        if not rows:
            raise AjaxException(
                f"❌ No se encontró ningún {nombre_sujeto} con ese {nombre_id}.",
                causa="Sin resultados",
            )
        sujeto = {
            clause.name: rows[0].get(clause.sql_name, "")
            for clause in selection_list.subject
        }

    if selection_list.web:
        subject_keys = [cl.sql_name for cl in (selection_list.subject or [])]
        objetos = [
            {k: v for k, v in row.items() if k not in subject_keys}
            for row in rows
            if any(row.get(k) is not None for k in row if k not in subject_keys)
        ]
        if not objetos:
            logger.info(f"Se encontró {nombre_sujeto}, pero sin {nombre_objetos}.")
            return {"sujeto": sujeto, "objetos": []}

    if sujeto:
        logger.info(f"Se encontraron datos de {nombre_sujeto}.")
    if objetos:
        logger.info(f"Se encontraron {len(objetos)} {nombre_objetos}.")
    return {"sujeto": sujeto, "objetos": objetos}


def parse_form(form: Type[Form], request: HttpRequest) -> Dict[str, Union[str, date]]:
    if request.content_type == "application/json":
        form_data = json.loads(request.body.decode("utf-8"))
        form_instance = form(form_data)
    else:
        form_instance = form(request.POST)

    if not form_instance.is_valid():
        logger.warning(
            f"Errores de validación en formulario: {form_instance.errors.as_json()}"
        )
        raise AjaxException()

    return dict(form_instance.cleaned_data.items())


def get_media_resources(
    objetos, context_list: ContextList, selection_list: SelectionList
) -> Dict:
    pdf_selection = selection_list.pdf or selection_list.web
    excel_selection = selection_list.excel or selection_list.web
    return {
        "pdf": asdict(context_list.pdf),
        "tabla_pdf": get.tabla(
            objetos=objetos, selection=pdf_selection, sql_selection=selection_list.sql
        ),
        "tabla_columnas_pdf": tuple(select.name for select in pdf_selection),
        "tabla_excel": get.tabla(
            objetos=objetos, selection=excel_selection, sql_selection=selection_list.sql
        ),
        "tabla_columnas_excel": tuple(select.name for select in excel_selection),
    }


def parse_queries(
    request: HttpRequest,
    form_data: Dict[str, Union[str, date]],
    context_list: ContextList,
    selection_list: SelectionList,
    exist_query: Optional[Callable] = None,
    data_query: Optional[Callable] = None,
    nombre_id: str = "",
    nombre_sujeto: str = "",
    nombre_objetos: str = "",
    *,
    model: Optional[Type[BaseModel]] = Consulta,
    api: bool = False,
    save_context: bool = True,
) -> Dict:
    id = form_data.get("id")
    fecha = form_data.get("fecha")

    ip_cliente = get.client_ip(request)
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    sujeto, objetos = get_objects(
        rows=get_rows(
            query_func=data_query,
            query_params=form_data,
        ),
        selection_list=selection_list,
        nombre_id=nombre_id,
        nombre_sujeto=nombre_sujeto,
        nombre_objetos=nombre_objetos,
    )

    selection = selection_list.api if api and selection_list.api else selection_list.web
    tabla = get.tabla(
        objetos=objetos,
        selection=selection,
        sql_selection=selection_list.sql,
    )
    tabla_columnas = tuple(select.name for select in selection)

    if model:
        model.objects.create(
            tipo=tipo,
            identificador=id,
            fecha_especificada=fecha,
            ip_cliente=ip_cliente,
            estado="Exitoso",
        )

    if save_context:
        request.session["context_data"] = {
            "sujeto": sujeto,
            "id": id,
            "fecha": (fecha.isoformat() if isinstance(fecha, date) else fecha),
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            **get_media_resources(objetos, context_list, selection_list),
        }

    return {"sujeto": sujeto, "tabla": tabla, "tabla_columnas": tabla_columnas}


@ajax_handler
def query_view(
    request: HttpRequest,
    context_list: ContextList,
    selection_list: SelectionList,
    form: Type[Form],
    data_query: Callable,
    nombre_objetos: str,
    *,
    model: Optional[Type[BaseModel]] = Consulta,
    nombre_id: Optional[str] = None,
    nombre_sujeto: Optional[str] = None,
    exist_query: Optional[Callable] = None,
    testing: bool = False,
) -> HttpResponse:
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    if testing:
        rows = 100
        text = "Ejemplo"
        sujeto = None
        tabla = tuple((text,) * len(selection_list.web) for _ in range(rows))
        tabla_columnas = tuple(select.name for select in selection_list.web)
        objetos = [
            {campo.sql_name: text for campo in selection_list.sql} for _ in range(rows)
        ]
        ajax_context = {
            "sujeto": sujeto,
            "tabla": tabla,
            "tabla_columnas": tabla_columnas,
        }

        request.session["context_data"] = {
            "sujeto": sujeto,
            "objetos": objetos,
            "id": "ID de ejemplo",
            "fecha": "2025-10-17",
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            **get_media_resources(objetos, context_list, selection_list),
        }

        logger.debug("Renderizando vista completa con contexto inicial.")
        return render(
            request,
            "queries/consulta_testing.html",
            {
                "initial": asdict(context_list.initial),
                "home_url": reverse_lazy(context_list.initial.home.url_name),
                "modal": asdict(context_list.modal),
                **ajax_context,
            },
        )

    if not testing and request.method == "POST":
        ajax_context = parse_queries(
            request=request,
            form_data=parse_form(form=form, request=request),
            context_list=context_list,
            selection_list=selection_list,
            exist_query=exist_query,
            data_query=data_query,
            nombre_id=nombre_id,
            nombre_sujeto=nombre_sujeto,
            nombre_objetos=nombre_objetos,
            model=model,
        )
        logger.debug(f"Datos de contexto procesados:\n{ajax_context}")

        if ajax_context.get("tabla"):
            raise AjaxException(
                context={"modal": asdict(context_list.modal), **ajax_context},
                filename="modal_buscar.html",
            )

    logger.debug("Renderizando vista completa con contexto inicial.")
    return render(
        request,
        "queries/consulta.html",
        {
            "initial": asdict(context_list.initial),
            "home_url": reverse_lazy(context_list.initial.home.url_name),
        },
    )
