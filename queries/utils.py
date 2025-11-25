import inspect
from dataclasses import asdict
from datetime import date, datetime
from pprint import pformat
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
from utils.get import formatted_campo
from utils.logger import get_logger
from .models import Consulta

logger = get_logger(__name__)
base_url = settings.WHATSAPP_API_BASE_URL


def whatsapp_status(url: str = f"{base_url}/status") -> Dict:
    try:
        return requests.get(url).json()
    except Exception:
        return {"status": "desconocido", "connected": False}


def evaluate_query(query: Callable, params: Dict) -> Tuple[str, Tuple[str, ...]]:
    sig = inspect.signature(query)
    return query(**{k: v for k, v in params.items() if k in sig.parameters})


from django.core.cache import cache
import hashlib
import json


def get_rows(
    query_func: Callable,
    query_params: Dict[str, Union[str, date]],
    db_name: str = "crit",
    cache_timeout: int = 300,
):
    key_raw = (
        f"{query_func.__name__}:{json.dumps(query_params, sort_keys=True, default=str)}"
    )
    cache_key = hashlib.sha256(key_raw.encode()).hexdigest()

    # Si está en caché
    cached = cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit for {cache_key}")
        return cached

    query, params = evaluate_query(query_func, query_params)
    logger.debug(f"Ejecutando consulta: '{query}', con parámetros: '{params}'.")

    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute(query, params)
            columnas = tuple(col[0] for col in cursor.description)
            rows = [dict(zip(columnas, row)) for row in cursor.fetchall()]
            cache.set(cache_key, rows, timeout=cache_timeout)  # Guardar en cache
            return rows
    except OperationalError as e:
        logger.error(f"No se pudo conectar con la base de datos: {e}")
        raise AjaxException("❌ No se pudo conectar con la base de datos.")
    except Exception as e:
        logger.exception(f"Error al obtener objetos: {str(e)}")
        raise AjaxException()


def object_of(row: Dict, subject_keys: List) -> Dict[str, str]:
    return {k: v for k, v in row.items() if k not in subject_keys}


def has_values(obj: Dict[str, str]) -> bool:
    return any(
        v is not None and (not isinstance(v, str) or v.strip() != "")
        for v in obj.values()
    )


def get_objects(
    rows: List[Dict],
    selection_list: SelectionList,
    id_name: str,
    subject_name: str,
    objects_name: str,
) -> Tuple[Optional[Dict[str, str]], List[Dict[str, str]]]:
    sujeto = None
    objetos: List[Dict[str, str]] = []

    if not rows:
        if selection_list.subject:
            raise AjaxException(
                f"❌ No se encontró ningún {subject_name} con ese {id_name}.",
                causa="Sin resultados",
            )
        else:
            raise AjaxException(
                f"❌ No se encontraron {objects_name}.", causa="Sin resultados"
            )

    if selection_list.subject:
        sujeto = {
            clause.name: formatted_campo(
                rows[0].get(clause.sql_name, ""), format_option=clause.format
            )
            for clause in selection_list.subject
        }
        logger.info(f"Se encontraron datos de {subject_name}.")

    if selection_list.web:
        subject_keys = [cl.sql_name for cl in (selection_list.subject or [])]
        objetos = [
            obj for row in rows if has_values(obj := object_of(row, subject_keys))
        ]
        if not objetos:
            logger.exception(f"No se encontraron {objects_name}.")
            raise AjaxException(
                f"❌ No se encontraron {objects_name}.", causa="Sin resultados"
            )
        logger.info(f"Se encontraron {len(objetos)} {objects_name}.")

    return sujeto, objetos


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
    subject: Dict[str, str],
    objects: List[Dict[str, str]],
    url_params: Dict[str, Union[str, date]],
    context_list: ContextList,
    selection_list: SelectionList,
) -> Dict[str, Union[str, Tuple[str, ...], Tuple[Tuple[str, ...], ...]]]:
    id = url_params.get("id")
    fecha = url_params.get("fecha")

    if isinstance(fecha, (date, datetime)):
        fecha = fecha.isoformat()

    pdf_selection = selection_list.pdf or selection_list.web
    excel_selection = selection_list.excel or selection_list.web

    return {
        "id": id,
        "fecha": (fecha.isoformat() if isinstance(fecha, datetime) else fecha),
        "sujeto": subject,
        "id_name": context_list.id_name,
        "subject_name": context_list.subject_name,
        "objects_name": context_list.objects_name,
        "pdf": asdict(context_list.pdf),
        "tabla_pdf": get.tabla(
            objetos=objects, selection=pdf_selection, sql_selection=selection_list.sql
        ),
        "tabla_columnas_pdf": tuple(select.name for select in pdf_selection),
        "tabla_excel": get.tabla(
            objetos=objects, selection=excel_selection, sql_selection=selection_list.sql
        ),
        "tabla_columnas_excel": tuple(select.name for select in excel_selection),
    }


def parse_queries(
    request: HttpRequest,
    form_data: Dict[str, Union[str, date]],
    context_list: ContextList,
    selection_list: SelectionList,
    data_query: Optional[Callable] = None,
    *,
    model: Optional[Type[BaseModel]] = Consulta,
    api: bool = False,
    save_context: bool = True,
) -> Dict:
    id = form_data.get("id")
    fecha = form_data.get("fecha")

    id_name = context_list.id_name
    subject_name = context_list.subject_name
    objects_name = context_list.objects_name

    client_ip = get.client_ip(request)
    query_type = get.model_type(objects_name=objects_name, subject_name=subject_name)

    subject, objects = get_objects(
        rows=get_rows(
            query_func=data_query,
            query_params=form_data,
        ),
        selection_list=selection_list,
        id_name=id_name,
        subject_name=subject_name,
        objects_name=objects_name,
    )
    logger.info(f"Datos de {subject_name}: {pformat(subject)}")
    logger.info(f"Datos de {objects_name}: {pformat(objects)}")

    selection = selection_list.api if api and selection_list.api else selection_list.web
    table = get.tabla(
        objetos=objects,
        selection=selection,
        sql_selection=selection_list.sql,
    )
    table_columns = tuple(select.name for select in selection)

    if model:
        model.objects.create(
            tipo=query_type,
            identificador=id,
            fecha_especificada=fecha,
            ip_cliente=client_ip,
            estado="Exitoso",
        )

    if save_context:
        request.session["context_data"] = get_media_resources(
            subject, objects, form_data, context_list, selection_list
        )

    return {"sujeto": subject, "tabla": table, "tabla_columnas": table_columns}


def initial_context(context_list: ContextList) -> Dict:
    context = {
        "initial": asdict(context_list.initial),
        "home_url": reverse_lazy(context_list.initial.home.url_name),
    }
    logger.debug(f"Initial context: {context}")
    return context


def modal_context(context_list: ContextList, ajax_context: Dict) -> Dict:
    context = {"modal": asdict(context_list.modal)} | ajax_context
    logger.debug(f"Modal context: {context}")
    return context


@ajax_handler
def query_view(
    request: HttpRequest,
    context_list: ContextList,
    selection_list: SelectionList,
    form: Type[Form],
    data_query: Callable,
    *,
    model: Optional[Type[BaseModel]] = Consulta,
    testing: bool = False,
) -> HttpResponse:
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    if testing:
        rows = 100
        text = "Ejemplo"
        subject = None
        table = tuple((text,) * len(selection_list.web) for _ in range(rows))
        column_tables = tuple(select.name for select in selection_list.web)
        objects = [
            {campo.sql_name: text for campo in selection_list.sql} for _ in range(rows)
        ]
        ajax_context = {
            "sujeto": subject,
            "tabla": table,
            "tabla_columnas": column_tables,
        }
        test_params = {
            "id": "ID de ejemplo",
            "fecha": "2025-10-17",
        }

        request.session["context_data"] = get_media_resources(
            subject, objects, test_params, context_list, selection_list
        )

        logger.debug("Renderizando vista completa con contexto inicial.")
        return render(
            request,
            "queries/consulta.html",
            initial_context(context_list) | modal_context(context_list, ajax_context),
        )

    if not testing and request.method == "POST":
        ajax_context = parse_queries(
            request=request,
            form_data=parse_form(form=form, request=request),
            context_list=context_list,
            selection_list=selection_list,
            data_query=data_query,
            model=model,
        )
        logger.debug(f"Datos de contexto procesados:\n{ajax_context}")

        if ajax_context.get("sujeto") or ajax_context.get("tabla"):
            raise AjaxException(
                context=modal_context(context_list, ajax_context),
                filename="modal_buscar.html",
            )

    logger.debug("Renderizando vista completa con contexto inicial.")
    return render(
        request,
        "queries/consulta.html",
        initial_context(context_list) | modal_context(context_list, {}),
    )
