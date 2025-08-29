import os
from typing import Dict, Optional, Callable

import requests
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from weasyprint import HTML

from .get_client import ip
from .logger import get_logger

logger = get_logger("parsers")

base_url = settings.WHATSAPP_API_BASE_URL


def mapear_columnas(data: Dict[str, Dict], mapeo: Dict[str, Dict]):
    campos = data.get("campos", {})
    mapeo_campos = mapeo["campos"]

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

    elif not resultado.get(f"{objetos}_sf"):
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
        context.update(**success_dict, **resultado)


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
        resultado = get_func(id, fecha=fecha)
        parse_result(
            resultado,
            context,
            fecha,
            success_dict=format_func(**resultado, campos=campos),
            identificador=identificador,
            persona=persona,
            objetos=objetos,
        )
        request.session["context_data"] = {
            c: context.get(c) for c in (f"{persona}_sf", f"{objetos}_sf")
        }
        model.objects.create(
            **{identificador: id}, fecha_especificada=fecha, ip_cliente=ip(request)
        )
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
    web_data: Dict,
    sql_data: Dict,
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
        **web_data.get("context", {}),
        "tabla_columnas": mapear_columnas(web_data, mapeo=sql_data),
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
            campos=web_data.get("campos", {}),
            form=form(request.POST),
            model=model,
            get_func=get_func,
            format_func=format_func,
            identificador=identificador,
            persona=persona,
            objetos=objetos,
        )
        print("A" * 1000, context, sep="\n", flush=True)
        if respuesta_ajax := ajax(
            request,
            context,
            persona=persona,
            partial=f"modal_{persona}.html",
        ):
            return respuesta_ajax

    return render(request, f"kiosco/buscar_{persona}.html", context)


def generar_pdf(
    identificador,
    format_func: Callable,
    pdf_data: Dict[str, Dict],
    sql_data: Dict[str, Dict],
    previous_context: Dict,
    persona: str,
) -> str:
    filename = f"{persona}_{identificador}.pdf"
    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    logger.debug(f"Generando PDF en: {output_path}")

    css_path = finders.find(f"kiosco/css/pdf_{persona}.css")
    css_files = [css_path] if css_path else []

    campos = pdf_data.get("campos", ())
    previous_context.update(
        format_func(**previous_context, campos=campos),
    )
    previous_context["tabla_columnas"] = mapear_columnas(pdf_data, mapeo=sql_data)

    html = render_to_string(
        f"kiosco/pdf_{persona}.html",
        {**pdf_data.get("context", {}), **previous_context},
    )
    HTML(string=html).write_pdf(output_path, stylesheets=css_files)
    logger.debug("PDF generado correctamente")

    return filename


def enviar_pdf(
    request,
    id: str,
    identificador: str,
    persona: str,
    format_func: Callable,
    pdf_data: Dict,
    sql_data: Dict,
    model,
):
    logger.debug(
        f"enviar_pdf_whatsapp called with method {request.method} and {identificador} {id}"
    )

    if request.method != "POST":
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero = request.POST.get("numero")
    logger.debug(f"Numero recibido: {numero}")
    if not numero:
        logger.error("Número de WhatsApp requerido no proporcionado")
        return JsonResponse({"error": "Número de WhatsApp requerido"}, status=400)

    web_context = request.session.get("context_data", {})
    filename = generar_pdf(
        id,
        persona=persona,
        format_func=format_func,
        pdf_data=pdf_data,
        sql_data=sql_data,
        previous_context=web_context,
    )

    # Mensaje WhatsApp
    mensaje = f"""Datos del {persona}:
Nombre: {web_context[persona]['Nombre']}
{identificador.title()}: {web_context[persona][identificador.title()]}"""

    payload = {
        "number": "521" + numero + "@c.us",
        "message": mensaje,
        "image_path": f"media/pdfs/{filename}",
    }

    try:
        response = requests.post(f"{base_url}/send-media", json=payload)
        data = response.json()
        logger.debug(f"Respuesta del microservicio: {data}")

        estado = "enviado" if response.status_code == 200 else "fallido"
        detalle_error = (
            None if estado == "enviado" else data.get("error", "Error desconocido")
        )

        model.objects.create(
            **{identificador: id},
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado=estado,
            detalle_error=detalle_error,
            ip_cliente=ip(request),
        )

        if estado == "enviado":
            logger.info("Mensaje enviado correctamente")
            return JsonResponse({"status": "enviado", "detalles": data})
        else:
            logger.error(f"Error enviando mensaje: {detalle_error}")
            return JsonResponse(
                {"status": "fallido", "error": detalle_error}, status=500
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con microservicio: {str(e)}", exc_info=True)
        model.objects.create(
            id,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado="fallido",
            detalle_error=str(e),
        )
        return JsonResponse(
            {"error": f"Error de conexión con microservicio: {str(e)}"}, status=500
        )
