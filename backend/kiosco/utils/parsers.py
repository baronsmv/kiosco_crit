from typing import Dict, Optional, Callable

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from .get_client import ip
from .logger import get_logger

logger = get_logger("views_parser")


def obtener_tabla(web: Dict[str, Dict], sql: Dict[str, Dict]):
    campos = web.get("campos", {})
    mapeo_campos = sql["campos"]

    for campo in campos:
        if campo not in mapeo_campos:
            raise ValueError(f"Campo desconocido: {campo}")

    return tuple(mapeo_campos[campo]["nombre"] for campo in campos)


def parse_result(
    resultado: Dict,
    context: Dict,
    fecha: Optional,
    success_dict: Dict,
    identificador: str,
    persona: str,
    objetos: str,
):
    if not resultado:
        context.update(
            {
                f"{identificador}_error": True,
                "error_target": identificador,
                "mensaje_error": f"❌ No se encontró ningún {persona} con ese {identificador}.",
            }
        )
        logger.warning(context["mensaje_error"])

    elif not resultado.get(objetos):
        error_context = {
            "mensaje_error": (
                f"❌ No se encontraron {objetos} con la fecha especificada."
                if fecha
                else f"❌ No se encontraron {objetos} activas para este {identificador}."
            ),
            "error_target": "fecha" if fecha else identificador,
        }

        context.update(error_context)
        context[error_context["error_target"] + "_error"] = True
        logger.info(error_context["mensaje_error"])

    else:
        context.update(**success_dict)


def parse_form(
    request,
    context: Dict,
    campos: Dict,
    form,
    model,
    get_func: Callable,
    format_func: Callable,
    identificador: str,
    persona: str,
    objetos: str,
):
    if form.is_valid():
        id = form.cleaned_data[identificador]
        fecha = form.cleaned_data["fecha"]
        context.update(
            {
                identificador: id,
                "fecha": fecha,
                f"{identificador}_proporcionado": True,
            }
        )
        resultado = get_func(id, fecha=fecha, campos=campos)
        parse_result(
            resultado,
            context,
            fecha,
            success_dict=format_func(**resultado, campos=campos),
            identificador=identificador,
            persona=persona,
            objetos=objetos,
        )
        model.objects.create(id, fecha_especificada=fecha, ip_cliente=ip(request))
    else:
        context.update(
            {
                f"{identificador}_error": bool(form[identificador].errors),
                "date_error": bool(form["fecha"].errors),
            }
        )
        logger.warning("Formulario inválido")


def ajax(
    request,
    context: Dict,
    persona: str,
    partial: str,
    partial_error: str = "mensaje_error.html",
):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = "kiosco/partials/"
        template += partial if context[persona] else partial_error
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)


def buscar(
    request,
    web: Dict,
    sql: Dict,
    form,
    model,
    get_func: Callable,
    format_func: Callable,
    identificador: str,
    persona: str,
    objetos: str,
):
    logger.info(f"Request method: {request.method}")
    logger.debug(f"POST data: {request.POST}")

    context = {
        **web.get("context", {}),
        "tabla_columnas": obtener_tabla(web=web, sql=sql),
        identificador: "",
        persona: None,
        f"{identificador}_proporcionado": False,
        f"{identificador}_error": False,
        "date_error": False,
        "mensaje_error": "",
        "error_target": "",
    }

    if request.method == "POST":
        parse_form(
            request,
            context,
            campos=web.get("campos", {}),
            form=form(request.POST),
            model=model,
            get_func=get_func,
            format_func=format_func,
            identificador=identificador,
            persona=persona,
            objetos=objetos,
        )
        if respuesta_ajax := ajax(
            request,
            context,
            persona=persona,
            partial=f"modal_{persona}.html",
        ):
            return respuesta_ajax

    return render(request, f"kiosco/buscar_{persona}.html", context)
