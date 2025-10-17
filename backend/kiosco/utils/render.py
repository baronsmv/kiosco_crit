from typing import Dict, Type, Callable, Optional

from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from .. import models
from ..utils import format, generate, get, validate
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
    partial_filename: str,
    partial_error: str = "mensaje_error.html",
) -> Optional[HttpResponse]:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = "kiosco/partials/"
        template += partial_filename if context["tabla"] else partial_error
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
    return None


def search(
    request: HttpRequest,
    config_data: Dict,
    form: Type[Form],
    data_query: Callable,
    nombre_objetos: str,
    model: Optional[Type[models.Base]] = models.Consulta,
    get_func: Callable = get.datos,
    format_func: Callable = format.campos,
    nombre_id: Optional[str] = None,
    nombre_sujeto: Optional[str] = None,
    exist_query: Optional[Callable] = None,
) -> HttpResponse:
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    context = get.initial_context(config_data)

    if request.method == "POST":
        validate.form(
            request=request,
            config_data=config_data,
            context=context,
            reg_form=form(request.POST),
            RegModel=model,
            exist_query=exist_query,
            data_query=data_query,
            get_func=get_func,
            format_func=format_func,
            nombre_id=nombre_id,
            nombre_sujeto=nombre_sujeto,
            nombre_objetos=nombre_objetos,
        )
        print(context, flush=True)

        if respuesta_ajax := ajax(
            request=request,
            context=context,
            partial_filename="modal_buscar.html",
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial.")
    return render(request, f"kiosco/buscar.html", context)


def pdf(request: HttpRequest) -> HttpResponse:
    abrir = request.GET.get("abrir") == "1"
    previous_context = request.session.get("context_data", {})

    filename = generate.pdf(
        previous_context=previous_context,
        format_func=format.campos,
        salida_a_color=False,
    )
    file_url = f"/media/pdfs/{filename}"

    if abrir:
        return HttpResponseRedirect(file_url)

    iframe_html = f"""
    <div style="height: 60vh; margin-top: 2rem; padding: 1rem;">
        <iframe src="{file_url}" width="100%" height="100%" style="border: none; border-radius: 8px;"></iframe>
    </div>
    """
    return JsonResponse({"html": iframe_html, "filename": filename})
