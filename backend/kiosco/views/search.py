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
    partial: str,
    partial_error: str = "mensaje_error.html",
) -> Optional[HttpResponse]:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = "kiosco/partials/"
        template += partial if context["persona"] else partial_error
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
    return None


def _render_search(
    request: HttpRequest,
    data: Dict,
    model: Type[Model],
    form: Type[Form],
    query_func: Callable,
    objetos: str,
    get_func: Callable = get.datos,
    format_func: Callable = format.campos,
    identificador: Optional[str] = None,
    persona: Optional[str] = None,
    exist_func: Optional[Callable] = None,
    pdf_url: Optional[str] = None,
) -> HttpResponse:
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    web_data = data["web"]
    sql_data = data["sql"]

    try:
        status_resp = requests.get(f"{base_url}/status")
        client_status = status_resp.json()
    except Exception:
        client_status = {"status": "desconocido", "connected": False}

    context = {
        **web_data.get("context", {}),
        "tipo": "_".join(filter(None, (objetos, persona))),
        "whatsapp_status": client_status,
        "tabla_columnas": map.columns(web_data, mapeo=sql_data),
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
            context=context,
            campos=web_data.get("campos", {}),
            sql_campos=sql_data.get("campos", {}),
            form=form(request.POST),
            model=model,
            exist_func=exist_func,
            get_func=get_func,
            query_func=query_func,
            format_func=format_func,
            identificador=identificador,
            persona=persona,
            objetos=objetos,
            pdf_url=(
                pdf_url
                if pdf_url
                else "_".join(filter(None, ("pdf", objetos, persona)))
            ),
        )

        if respuesta_ajax := _render_ajax(
            request,
            context,
            partial="modal_buscar.html",
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial")
    return render(request, f"kiosco/buscar.html", context)


def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return _render_search(
        request=request,
        data=config.cfg_espacios,
        model=models.EspaciosVaciosConsulta,
        form=forms.BuscarFechaForm,
        query_func=queries.data.espacios_disponibles,
        objetos="espacios",
    )


def citas_colaborador(request: HttpRequest) -> HttpResponse:
    return _render_search(
        request=request,
        data=config.cfg_citas_colaborador,
        model=models.CitasColaboradorConsulta,
        form=forms.BuscarIdFechaForm,
        exist_func=queries.exist.colaborador,
        query_func=queries.data.citas_colaborador,
        identificador="nombre de usuario",
        persona="colaborador",
        objetos="citas",
    )


def citas_paciente(request: HttpRequest) -> HttpResponse:
    return _render_search(
        request=request,
        data=config.cfg_citas_paciente,
        model=models.CitasCarnetConsulta,
        form=forms.BuscarIdFechaForm,
        exist_func=queries.exist.paciente,
        query_func=queries.data.citas_carnet,
        identificador="carnet",
        persona="paciente",
        objetos="citas",
    )
