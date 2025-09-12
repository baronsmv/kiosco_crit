import os
from datetime import datetime
from typing import Callable, Dict
from typing import Optional

import requests
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from weasyprint import HTML

from .get_client import ip
from .logger import get_logger

logger = get_logger(__name__)

base_url = settings.WHATSAPP_API_BASE_URL


def mapear_columnas(data: Dict[str, Dict], mapeo: Dict[str, Dict]):
    campos = data.get("campos", {})
    mapeo_campos = mapeo["campos"]

    logger.debug(f"Mapeando columnas: {list(campos)}")

    for campo in campos:
        if campo not in mapeo_campos:
            logger.error(f"Campo desconocido en mapeo: {campo}")
            raise ValueError(f"Campo desconocido: {campo}")

    columnas = tuple(mapeo_campos[campo]["nombre"] for campo in campos)
    logger.debug(f"Columnas mapeadas: {columnas}")
    return columnas


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
                "id_error": True,
                "error_target": "id",
                "mensaje_error": f"❌ No se encontró ningún {persona} con ese {identificador}.",
            }
        )
        logger.warning(f"ID inválido: {identificador} - No se encontró {persona}")

    elif not resultado.get(f"objetos_sf"):
        error_context = {
            "mensaje_error": (
                f"❌ No se encontraron {objetos} con la fecha especificada."
                if fecha
                else f"❌ No se encontraron {objetos} activas para este {identificador}."
            ),
            "error_target": "fecha" if fecha else "id",
        }

        context.update(error_context)
        context[error_context["error_target"] + "_error"] = True
        logger.info(f"Sin resultados para {objetos} con ID {identificador}")

    elif success_dict:
        context.update(**success_dict, **resultado)
        logger.info(
            f"{objetos.capitalize()} encontrados exitosamente para ID {identificador}"
        )


def parse_form(
    request,
    context: Dict,
    campos: Dict,
    sql_campos: Dict,
    form,
    model,
    exist_func: Callable,
    get_func: Callable,
    query_func: Callable,
    format_func: Callable,
    identificador: str,
    persona: str,
    objetos: str,
    pdf_url: str,
):
    if form.is_valid():
        logger.debug(f"Formulario válido. Procesando ID: {form.cleaned_data['id']}")
        id = form.cleaned_data["id"]
        fecha = form.cleaned_data["fecha"]
        context.update(
            {
                "id": id,
                "id_proporcionado": True,
                "fecha": fecha,
                "pdf_url": reverse(pdf_url, args=(id,)),
            }
        )
        resultado = get_func(
            id,
            sql_campos=sql_campos,
            exist_func=exist_func,
            query_func=query_func,
            fecha=fecha,
        )
        parse_result(
            resultado,
            context,
            fecha,
            success_dict=(
                format_func(
                    **resultado,
                    campos=campos,
                    persona=persona,
                    identificador=identificador,
                )
                if resultado
                else None
            ),
            identificador=identificador,
            persona=persona,
            objetos=objetos,
        )
        request.session["context_data"] = {
            c: context.get(c) for c in ("persona_sf", "objetos_sf")
        }
        model.objects.create(
            identificador=id, fecha_especificada=fecha, ip_cliente=ip(request)
        )
        logger.info(f"{persona.capitalize()} encontrado y datos almacenados en sesión")
    else:
        context.update(
            {
                "id_error": bool(form[identificador].errors),
                "date_error": bool(form["fecha"].errors),
            }
        )
        logger.warning(f"Errores de validación en formulario: {form.errors.as_json()}")


def ajax_buscar(
    request,
    context: Dict,
    partial: str,
    partial_error: str = "mensaje_error.html",
):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = "kiosco/partials/"
        template += partial if context["persona"] else partial_error
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)


def buscar(
    request,
    data: Dict,
    form,
    model,
    exist_func: Callable,
    get_func: Callable,
    query_func: Callable,
    format_func: Callable,
    identificador: str,
    persona: str,
    objetos: str,
    pdf_url: str,
    fecha_inicial: Optional[datetime.date] = None,
    auto_borrado: bool = False,
    mostrar_imprimir: bool = True,
    mostrar_inicio: bool = True,
):
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
        "home_url": reverse("home"),
        "tipo": persona,
        "fecha_inicial": fecha_inicial,
        "auto_borrado": auto_borrado,
        "mostrar_imprimir": mostrar_imprimir,
        "mostrar_inicio": mostrar_inicio,
        "whatsapp_status": client_status,
        "tabla_columnas": mapear_columnas(web_data, mapeo=sql_data),
        "id": "",
        "persona": None,
        "id_proporcionado": False,
        "id_error": False,
        "date_error": False,
        "mensaje_error": "",
        "error_target": "",
    }

    if request.method == "POST":
        parse_form(
            request,
            context,
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
            pdf_url=pdf_url,
        )
        if respuesta_ajax := ajax_buscar(
            request,
            context,
            partial=f"modal_buscar.html",
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial")
    return render(request, f"kiosco/buscar.html", context)


import hashlib


def generar_pdf(
    id: str,
    format_func: Callable,
    data: Dict[str, Dict],
    previous_context: Dict,
    persona: str,
    identificador: str,
) -> str:
    pdf_data = data["pdf"]
    sql_data = data["sql"]

    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)

    if not previous_context:
        logger.error("previous_context está vacío. No se puede generar PDF.")
        raise ValueError("No hay datos de contexto en sesión.")

    logger.debug(f"Contexto recibido en generar_pdf: {previous_context.keys()}")

    try:
        formatted_context = format_func(
            **previous_context,
            campos=pdf_data.get("campos", ()),
            persona=persona,
            identificador=identificador,
        )
        previous_context.update(formatted_context)
    except Exception:
        logger.exception("Error al aplicar format_func en generar_pdf")
        raise

    # Render HTML
    try:
        html = render_to_string(
            "kiosco/pdf.html",
            {
                **pdf_data.get("context", {}),
                **previous_context,
                "tabla_columnas": mapear_columnas(pdf_data, mapeo=sql_data),
            },
        )
    except Exception:
        logger.exception("Error al renderizar HTML")
        raise

    # Calcular hash del contenido HTML
    content_hash = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    filename = f"{persona}_{id}_{content_hash}.pdf"
    output_path = os.path.join(output_dir, filename)
    logger.debug(f"Generando PDF en: {output_path}")

    # Buscar CSS
    css_path = finders.find(f"kiosco/css/pdf.css")
    css_files = [css_path] if css_path else []

    try:
        HTML(string=html).write_pdf(output_path, stylesheets=css_files)
        logger.debug("PDF generado correctamente")
    except Exception as e:
        logger.exception("Error al generar el PDF")
        raise

    if not os.path.exists(output_path):
        logger.error(f"El archivo PDF no fue creado: {output_path}")
        raise FileNotFoundError("No se pudo generar el archivo PDF.")

    return filename


def enviar_pdf(
    request,
    id: str,
    identificador: str,
    persona: str,
    format_func: Callable,
    data: Dict,
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
        id=id,
        format_func=format_func,
        data=data,
        previous_context=web_context,
        persona=persona,
        identificador=identificador,
    )

    # Mensaje WhatsApp
    mensaje = f"""Datos del {persona}:
Nombre: {web_context['persona']['Nombre']}
{identificador.title()}: {web_context['persona'][identificador.title()]}"""

    payload = {
        "number": "521" + numero + "@c.us",
        "message": mensaje,
        "image_path": f"media/pdfs/{filename}",
    }

    try:
        response = requests.post(f"{base_url}/send-media", json=payload)
        response_data = response.json()
        logger.debug(f"Respuesta del microservicio: {response_data}")

        estado = "enviado" if response.status_code == 200 else "fallido"
        detalle_error = (
            None
            if estado == "enviado"
            else response_data.get("error", "Error desconocido")
        )

        model.objects.create(
            identificador=id,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado=estado,
            detalle_error=detalle_error,
            ip_cliente=ip(request),
        )

        if estado == "enviado":
            logger.info("Mensaje enviado correctamente")
            return JsonResponse({"status": "enviado", "detalles": response_data})
        else:
            logger.error(f"Error enviando mensaje: {detalle_error}")
            return JsonResponse(
                {"status": "fallido", "error": detalle_error}, status=500
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con microservicio: {str(e)}", exc_info=True)
        model.objects.create(
            identificador=id,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado="fallido",
            detalle_error=str(e),
        )
        return JsonResponse(
            {"error": f"Error de conexión con microservicio: {str(e)}"}, status=500
        )
