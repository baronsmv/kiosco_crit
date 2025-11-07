from datetime import date
from typing import Callable, Dict, Optional, Type

from django.db import OperationalError
from django.forms import Form
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render

from classes import models
from classes.exceptions import AjaxException
from classes.models import BaseModel
from utils import get, validate
from utils.logger import get_logger
from utils.render import ajax_response
from .models import Consulta

logger = get_logger(__name__)


def parse_form(
    request: HttpRequest,
    context: Dict,
    config_data: Dict,
    form: Form,
    model: Optional[Type[models.BaseModel]],
    exist_query: Optional[Callable],
    data_query: Callable,
    nombre_id: str = "",
    nombre_sujeto: str = "",
    nombre_objetos: str = "",
) -> None:
    form_fields = form.fields.keys()
    has_id = "id" in form_fields
    has_fecha = "fecha" in form_fields
    ip_cliente = get.client_ip(request)
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    web_data = config_data["web"]
    pdf_data = config_data["pdf"]
    sql_data = config_data["sql"]

    if not form.is_valid():
        logger.warning(f"Errores de validación en formulario: {form.errors.as_json()}")
        raise AjaxException()

    id = form.cleaned_data["id"] if has_id else None
    fecha = form.cleaned_data["fecha"] if has_fecha else None

    if has_id and not validate.id(
        id=id,
        fecha=fecha,
        has_fecha=has_fecha,
        context=context,
        model=model,
        reg_form=form,
        ip_cliente=ip_cliente,
        tipo=tipo,
    ):
        raise AjaxException(f"{nombre_id.capitalize()} no válido.")

    context.update({"id": id or "", "fecha": fecha})

    try:
        sujeto = get.subject(
            id,
            exist_query=exist_query,
            nombre_sujeto=nombre_sujeto,
            nombre_id=nombre_id,
        )
        objetos = get.all_objects(
            id,
            fecha,
            data_query=data_query,
            nombre_objetos=nombre_objetos,
            nombre_id=nombre_id,
        )
    except OperationalError as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        if model:
            model.objects.create(
                tipo=tipo,
                identificador=id if has_id else None,
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado="Error de conexión",
            )
        raise AjaxException("❌ No se pudo conectar con la base de datos.")
    except AjaxException as e:
        if model:
            model.objects.create(
                tipo=tipo,
                identificador=id if has_id else None,
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado=e.causa,
            )
        raise

    context["sujeto"] = sujeto
    context["tabla"] = get.filtered_objects(
        objetos,
        campos=web_data.get("campos", {}),
        sql_campos=sql_data.get("campos", {}),
    )

    if model:
        model.objects.create(
            tipo=tipo,
            **({"identificador": id} if has_id else {}),
            fecha_especificada=fecha,
            ip_cliente=ip_cliente,
            estado="Exitoso",
        )

    request.session["context_data"] = {
        "sujeto": sujeto,
        "tabla": context.get("tabla"),
        "objetos": objetos,
        "id": id or "",
        "fecha": (fecha.isoformat() if isinstance(fecha, date) else fecha),
        "nombre_objetos": nombre_objetos,
        "nombre_sujeto": nombre_sujeto,
        "nombre_id": nombre_id,
        "pdf_data": pdf_data,
        "sql_data": sql_data,
    }


def query_view(
    request: HttpRequest,
    config_data: Dict,
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

    context = get.initial_context(config_data)

    if testing:
        context["tabla"] = tuple(("Ejemplo",) * 5 for _ in range(100))
        request.session["context_data"] = {
            "sujeto": None,
            "tabla": context["tabla"],
            "id": "ID de ejemplo",
            "fecha": "2025-10-17",
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            "pdf_data": config_data["pdf"],
            "sql_data": config_data["sql"],
        }
        model = None

    if not testing and request.method == "POST":
        try:
            parse_form(
                request=request,
                config_data=config_data,
                context=context,
                form=form(request.POST),
                model=model,
                exist_query=exist_query,
                data_query=data_query,
                nombre_id=nombre_id,
                nombre_sujeto=nombre_sujeto,
                nombre_objetos=nombre_objetos,
            )
            logger.debug(f"Datos de contexto procesados:\n{context}")
        except AjaxException as e:
            return ajax_response(request, context=e.context())

        if respuesta_ajax := ajax_response(
            request=request,
            context=context,
            filename=("modal_buscar.html" if context.get("tabla") else "status.html"),
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial.")
    return render(request, f"queries/consulta.html", context)
