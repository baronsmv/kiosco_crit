from datetime import date
from typing import Dict, Type, Callable, Optional

import requests
from django.conf import settings
from django.db.models import Model
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from .. import models, forms, queries
from ..utils import config, format, map, get, validate
from ..utils.logger import get_logger

logger = get_logger(__name__)
base_url = settings.WHATSAPP_API_BASE_URL


def _render_ajax(
    request: HttpRequest,
    context: Dict,
    partial_filename: str,
    partial_error: str = "mensaje_error.html",
) -> Optional[HttpResponse]:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = "kiosco/partials/"
        template += partial_filename if context["persona"] else partial_error
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
    return None


def _render_search(
    request: HttpRequest,
    config_data: Dict,
    RegModel: Type[Model],
    RegForm: Type[Form],
    query_func: Callable,
    nombre_objetos: str,
    get_func: Callable = get.datos,
    format_func: Callable = format.campos,
    nombre_id: Optional[str] = None,
    nombre_sujeto: Optional[str] = None,
    exist_func: Optional[Callable] = None,
    pdf_url: Optional[str] = None,
) -> HttpResponse:
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    web_data = config_data["web"]
    sql_data = config_data["sql"]

    try:
        status_resp = requests.get(f"{base_url}/status")
        client_status = status_resp.json()
    except Exception:
        client_status = {"status": "desconocido", "connected": False}

    context = {
        **web_data.get("context", {}),
        "tipo": "_".join(filter(None, (nombre_objetos, nombre_sujeto))),
        "whatsapp_status": client_status,
        "tabla_columnas": map.columns(web_data, sql_data=sql_data),
        "id": "",
        "persona": None,
        "id_proporcionado": False,
        "id_error": False,
        "date_error": False,
        "mensaje_error": "",
        "error_target": "",
    }
    context["home_url"] = reverse_lazy(context.get("home_url", "home"))
    context["fecha_inicial"] = (
        date.today() if context.get("fecha_inicial", False) else ""
    )

    if request.method == "POST":
        validate.form(
            request=request,
            config_data=config_data,
            context=context,
            reg_form=RegForm(request.POST),
            RegModel=RegModel,
            exist_func=exist_func,
            get_func=get_func,
            query_func=query_func,
            format_func=format_func,
            nombre_id=nombre_id,
            nombre_persona=nombre_sujeto,
            nombre_objetos=nombre_objetos,
            pdf_url=(
                pdf_url
                if pdf_url
                else "_".join(
                    filter(None, ("pdf", nombre_objetos, nombre_sujeto))
                ).replace(" ", "_")
            ),
        )

        if respuesta_ajax := _render_ajax(
            request,
            context,
            partial_filename="modal_buscar.html",
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial")
    return render(request, f"kiosco/buscar.html", context)


def citas_paciente(request: HttpRequest) -> HttpResponse:
    return _render_search(
        request=request,
        config_data=config.cfg_citas_paciente,
        RegModel=models.CitasCarnetConsulta,
        RegForm=forms.BuscarIdFechaForm,
        exist_func=queries.exist.paciente,
        query_func=queries.data.citas_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="citas",
    )


def citas_colaborador(request: HttpRequest) -> HttpResponse:
    return _render_search(
        request=request,
        config_data=config.cfg_citas_colaborador,
        RegModel=models.CitasColaboradorConsulta,
        RegForm=forms.BuscarIdFechaForm,
        exist_func=queries.exist.colaborador,
        query_func=queries.data.citas_colaborador,
        nombre_id="nombre de usuario",
        nombre_sujeto="colaborador",
        nombre_objetos="citas",
    )


def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return _render_search(
        request=request,
        config_data=config.cfg_espacios_disponibles,
        RegModel=models.EspaciosVaciosConsulta,
        RegForm=forms.BuscarFechaForm,
        query_func=queries.data.espacios_disponibles,
        nombre_objetos="espacios disponibles",
    )
