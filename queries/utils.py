from datetime import date
from typing import Callable, Dict, Optional, Type

from django.forms import Form
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import render

from classes import models
from classes.exceptions import AjaxException
from classes.models import BaseModel
from utils import get, validate
from utils.decorators import ajax_handler
from utils.logger import get_logger
from .models import Consulta

logger = get_logger(__name__)


def parse_form(form: Form):
    if not form.is_valid():
        logger.warning(f"Errores de validación en formulario: {form.errors.as_json()}")
        raise AjaxException()

    return dict(form.cleaned_data.items())


def parse_queries(
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
    form_data = parse_form(form)
    id = form_data.get("id")
    fecha = form_data.get("fecha")
    context.update(form_data)

    ip_cliente = get.client_ip(request)
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    web_data = config_data["web"]
    pdf_data = config_data["pdf"]
    sql_data = config_data["sql"]

    if id:
        if not validate.id(id=id, context=context):
            raise AjaxException(f"{nombre_id.capitalize()} no válido.")

        sujeto = get.subject(
            id=id,
            exist_query=exist_query,
            nombre_sujeto=nombre_sujeto,
            nombre_id=nombre_id,
            tipo=tipo,
            ip_cliente=ip_cliente,
        )
    else:
        sujeto = None

    objetos = get.all_objects(
        data=form_data,
        data_query=data_query,
        nombre_objetos=nombre_objetos,
        nombre_id=nombre_id,
        tipo=tipo,
        ip_cliente=ip_cliente,
    )
    context["tabla"] = get.filtered_objects(
        objetos,
        campos=web_data.get("campos", {}),
        sql_campos=sql_data.get("campos", {}),
    )

    if model:
        model.objects.create(
            tipo=tipo,
            identificador=id,
            fecha_especificada=fecha,
            ip_cliente=ip_cliente,
            estado="Exitoso",
        )

    request.session["context_data"] = {
        "sujeto": sujeto,
        "objetos": objetos,
        "id": id,
        "fecha": (fecha.isoformat() if isinstance(fecha, date) else fecha),
        "nombre_objetos": nombre_objetos,
        "nombre_sujeto": nombre_sujeto,
        "nombre_id": nombre_id,
        "pdf_data": pdf_data,
        "sql_data": sql_data,
    }


@ajax_handler
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
    TESTING: bool = False,
) -> HttpResponse:
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    context = get.initial_context(config_data)

    if TESTING:
        rows = 100
        text = "Ejemplo"
        sql_campos = config_data["sql"]["campos"]
        model = None
        context.update(
            {
                "tabla": tuple((text,) * len(sql_campos) for _ in range(rows)),
                "objetos": [{campo: text for campo in sql_campos} for _ in range(rows)],
            }
        )

        request.session["context_data"] = {
            "sujeto": None,
            "tabla": context["tabla"],
            "objetos": context["objetos"],
            "id": "ID de ejemplo",
            "fecha": "2025-10-17",
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            "pdf_data": config_data["pdf"],
            "sql_data": config_data["sql"],
        }

    if not TESTING and request.method == "POST":
        parse_queries(
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

        if context.get("tabla"):
            raise AjaxException(context=context, filename="modal_buscar.html")

    logger.debug("Renderizando vista completa con contexto inicial.")
    return render(request, f"queries/consulta.html", context)
