import inspect
import json
from dataclasses import asdict
from datetime import date
from typing import Callable, Dict, List, Optional, Tuple, Union
from typing import Type

import requests
from django.conf import settings
from django.db import connections, OperationalError
from django.forms import Form
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from classes.contexts import IdSubContext, ContextList
from classes.exceptions import AjaxException
from classes.models import BaseModel
from classes.selections import SelectionList
from utils import get, validate
from utils.decorators import ajax_handler, query_handler
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


def evaluate_query(data: Dict, func: Callable) -> Tuple[str, Tuple[str, ...]]:
    sig = inspect.signature(func)
    return func(**{k: v for k, v in data.items() if k in sig.parameters})


@query_handler
def get_subject(
    id: Optional[str],
    exist_query: Optional[Callable],
    nombre_sujeto: str,
    nombre_id: str,
    id_context: IdSubContext,
    *,
    db_name: str = "crit",
    **_,
) -> Optional[Dict[str, str]]:
    if not id or not exist_query:
        logger.info(f"ID o query de {nombre_sujeto} no configurados.")
        return None

    if not validate.id_by_context(id=id, id_context=id_context):
        raise AjaxException(f"{nombre_id.capitalize()} no válido.")

    logger.info(f"Buscando datos para {nombre_sujeto} con {nombre_id}: '{id}'")

    try:
        with connections[db_name].cursor() as cursor:
            sujeto = exist_query(id, cursor) if exist_query else None
    except OperationalError as e:
        logger.error(f"Error al obtener datos para ID: '{id}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Error al obtener datos del ID: '{id}': {str(e)}")
        raise AjaxException()

    if not sujeto:
        message = f"❌ No se encontró ningún {nombre_sujeto} con ese {nombre_id}."
        logger.info(message)
        raise AjaxException(message, causa="ID Inexistente")

    return {
        f"Nombre de {nombre_sujeto.capitalize()}": sujeto.get("nombre", "").title(),
        nombre_id.capitalize(): sujeto.get("id", ""),
    }


@query_handler
def get_objects(
    data: Dict[str, Union[str, date]],
    data_query: Optional[Callable],
    nombre_objetos: str,
    nombre_id: str,
    *,
    db_name: str = "crit",
    **_,
) -> Optional[List[Dict]]:
    if not data or not data_query:
        return None

    query, params = evaluate_query(data, data_query)
    logger.debug(f"Ejecutando consulta: '{query}', con parámetros: '{params}'.")

    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute(query, params)
            columnas = tuple(col[0] for col in cursor.description)
            objetos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except OperationalError as e:
        logger.error(f"Error al obtener objetos para ID: '{id}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Error al obtener objetos para ID: '{id}': {str(e)}")
        raise AjaxException()

    if not objetos:
        if "fecha" in data:
            message = (
                f"❌ No se encontraron {nombre_objetos} con la fecha especificada."
            )
        else:
            message = f"❌ No se encontraron {nombre_objetos} para este {nombre_id}."
        logger.info(message)
        raise AjaxException(
            message, target="fecha" if "fecha" in data else "id", causa="Sin resultados"
        )

    logger.info(f"Se encontraron {len(objetos)} objetos.")
    return objetos


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
    save_context: bool = True,
) -> Dict:
    id = form_data.get("id")
    fecha = form_data.get("fecha")

    ip_cliente = get.client_ip(request)
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    sujeto = get_subject(
        id=id,
        exist_query=exist_query,
        nombre_sujeto=nombre_sujeto,
        nombre_id=nombre_id,
        id_context=context_list.initial.id,
        tipo=tipo,
        ip_cliente=ip_cliente,
    )
    objetos = get_objects(
        data=form_data,
        data_query=data_query,
        nombre_objetos=nombre_objetos,
        nombre_id=nombre_id,
        tipo=tipo,
        ip_cliente=ip_cliente,
    )
    tabla = get.tabla(
        objetos=objetos, selection=selection_list.web, sql_selection=selection_list.sql
    )
    tabla_columnas = tuple(select.name for select in selection_list.web)

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
            "objetos": objetos,
            "id": id,
            "fecha": (fecha.isoformat() if isinstance(fecha, date) else fecha),
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            "pdf_context": asdict(context_list.pdf),
            "pdf_selection": tuple(asdict(s) for s in selection_list.pdf),
            "sql_selection": tuple(asdict(s) for s in selection_list.sql),
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

        request.session["context_data"] = {
            "sujeto": None,
            "tabla": tuple((text,) * len(selection_list.web) for _ in range(rows)),
            "objetos": [
                {campo: text for campo in selection_list.sql} for _ in range(rows)
            ],
            "id": "ID de ejemplo",
            "fecha": "2025-10-17",
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            "context_list": context_list,
            "selections": selection_list,
        }

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
        f"queries/consulta.html",
        {
            "initial": asdict(context_list.initial),
            "home_url": reverse_lazy(context_list.initial.home.url),
        },
    )
