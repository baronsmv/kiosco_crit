from typing import Dict, Type, Callable, Optional

from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from .. import models
from ..utils import format, generate, get, parse
from ..utils.logger import get_logger

logger = get_logger(__name__)


def menu(request: HttpRequest, config: Dict[str, Dict]) -> HttpResponse:
    menu_options = tuple(
        (
            reverse_lazy(key),
            option.get("title", ""),
            option.get("description", ""),
        )
        for key, option in config.get("options", {}).items()
    )
    return render(
        request,
        "kiosco/menu.html",
        config.get("context", {})
        | {"home_url": reverse_lazy("home"), "menu_options": menu_options},
    )


def ajax(
    request: HttpRequest,
    context: Dict,
    *,
    filename: str = "status.html",
) -> Optional[HttpResponse]:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = f"kiosco/partials/{filename}"
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
    logger.info("Petición no AJAX recibida (probablemente vista inicial).")
    return None


def search(
    request: HttpRequest,
    config_data: Dict,
    form: Type[Form],
    data_query: Callable,
    nombre_objetos: str,
    *,
    model: Optional[Type[models.Base]] = models.Consulta,
    get_func: Callable = get.datos,
    format_func: Callable = format.campos,
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
        parse.form(
            request=request,
            config_data=config_data,
            context=context,
            form=form(request.POST),
            model=model,
            exist_query=exist_query,
            data_query=data_query,
            get_func=get_func,
            format_func=format_func,
            nombre_id=nombre_id,
            nombre_sujeto=nombre_sujeto,
            nombre_objetos=nombre_objetos,
        )
        logger.debug(f"Datos de contexto procesados:\n{context}")

        if respuesta_ajax := ajax(
            request=request,
            context=context,
            filename=("modal_buscar.html" if context.get("tabla") else "status.html"),
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial.")
    return render(request, f"kiosco/buscar.html", context)


def pdf(request: HttpRequest) -> HttpResponse:
    filename = generate.pdf(request.session.get("context_data", {}), color=False)
    file_url = f"/media/pdf/{filename}"

    if request.GET.get("abrir") == "1":
        return HttpResponseRedirect(file_url)

    iframe_html = f"""
    <div style="height: 60vh; margin-top: 2rem; padding: 1rem;">
        <iframe src="{file_url}" width="100%" height="100%" style="border: none; border-radius: 8px;"></iframe>
    </div>
    """
    return JsonResponse({"html": iframe_html, "filename": filename})


def excel(request: HttpRequest) -> HttpResponse:
    filename = generate.excel(request.session.get("context_data", {}))
    file_url = f"/media/excel/{filename}"

    return HttpResponseRedirect(file_url)
