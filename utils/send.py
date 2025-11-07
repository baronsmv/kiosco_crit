from typing import Type

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.http import HttpRequest, HttpResponse, JsonResponse

from classes.models import BaseModel
from sendings import models
from utils import generate, get, render
from utils.logger import get_logger

logger = get_logger(__name__)

base_url = settings.WHATSAPP_API_BASE_URL


def pdf_email(
    request: HttpRequest,
    model: Type[BaseModel] = models.EnvioEmail,
) -> HttpResponse | JsonResponse:
    previous_context = request.session.get("context_data", {})
    id = previous_context.get("id", "")
    nombre_sujeto = previous_context.get("nombre_sujeto", "")
    nombre_objetos = previous_context.get("nombre_objetos", "")
    fecha_especificada = previous_context.get("fecha")
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    if request.method != "POST":
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    correo = request.POST.get("email")
    logger.debug(f"Email recibido: {correo}")

    try:
        validate_email(correo)
    except ValidationError:
        logger.error("Email inválido")
        return render.ajax(
            request,
            context={
                "mensaje_ajax": "Dirección de correo inválida.",
                "tipo_ajax": "error",
            },
        ) or JsonResponse({"error": "Email inválido"}, status=400)

    filename = generate.pdf(previous_context, color=True)
    subject = f"Datos del {nombre_sujeto}"
    body = "Adjuntamos el archivo solicitado en formato PDF."
    mensaje = "\n".join((subject, body))
    pdf_path = f"media/pdf/{filename}"

    try:
        email = EmailMessage(subject, body, to=[correo])
        email.attach_file(pdf_path)
        email.send()
    except Exception as e:
        logger.exception("Error enviando correo")
        if model:
            model.objects.create(
                tipo=tipo,
                **({"identificador": id} if id else {}),
                fecha_especificada=fecha_especificada,
                ip_cliente=get.client_ip(request),
                correo_destino=correo,
                mensaje=mensaje,
                archivo_pdf=pdf_path,
                estado="Fallido",
                detalle_error=str(e),
            )
        return render.ajax(
            request,
            context={
                "mensaje_ajax": "Ocurrió un error al enviar el correo.",
                "tipo_ajax": "error",
            },
        ) or JsonResponse({"error": str(e)}, status=500)

    if model:
        model.objects.create(
            tipo=tipo,
            **({"identificador": id} if id else {}),
            fecha_especificada=fecha_especificada,
            ip_cliente=get.client_ip(request),
            correo_destino=correo,
            mensaje=mensaje,
            archivo_pdf=pdf_path,
            estado="Enviado",
        )
    return render.ajax(
        request,
        context={
            "mensaje_ajax": "Correo enviado exitosamente.",
            "tipo_ajax": "success",
        },
    ) or JsonResponse({"status": "enviado"})


def pdf_whatsapp(
    request: HttpRequest,
    model: Type[BaseModel] = models.EnvioWhatsapp,
) -> JsonResponse:
    previous_context = request.session.get("context_data", {})
    id = previous_context.get("id", "")
    sujeto = previous_context.get("sujeto", {})
    nombre_id = previous_context.get("nombre_id")
    nombre_sujeto = previous_context.get("nombre_sujeto")
    nombre_objetos = previous_context.get("nombre_objetos", "")
    fecha_especificada = previous_context.get("fecha", None)
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    logger.debug(
        f"enviar_pdf_whatsapp called with method {request.method} and {nombre_id} {id}"
    )

    if request.method != "POST":
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero = request.POST.get("numero")
    logger.debug(f"Numero recibido: {numero}")
    if not numero:
        logger.error("Número de WhatsApp requerido no proporcionado")
        return JsonResponse({"error": "Número de WhatsApp requerido"}, status=400)

    filename = generate.pdf(previous_context, color=True)
    mensaje = f"""Datos del {nombre_sujeto}:
Nombre: {sujeto['Nombre']}
{nombre_id.title()}: {sujeto[nombre_id.title()]}"""
    payload = get.whatsapp_payload(number=numero, mensaje=mensaje, filename=filename)

    try:
        response = requests.post(f"{base_url}/send-media", json=payload)
        response_data = response.json()
        logger.debug(f"Respuesta del microservicio: {response_data}")

        estado = "Enviado" if response.status_code == 200 else "Fallido"
        detalle_error = (
            None
            if estado == "enviado"
            else response_data.get("error", "Error desconocido")
        )

        if model:
            model.objects.create(
                tipo=tipo,
                **({"identificador": id} if id else {}),
                fecha_especificada=fecha_especificada,
                ip_cliente=get.client_ip(request),
                numero_destino=numero,
                mensaje=mensaje,
                archivo_pdf=payload["image_path"],
                estado=estado,
                detalle_error=detalle_error,
            )

        if estado == "Enviado":
            logger.info("Mensaje enviado correctamente")
            return JsonResponse({"status": "enviado", "detalles": response_data})
        else:
            logger.error(f"Error enviando mensaje: {detalle_error}")
            return JsonResponse(
                {"status": "fallido", "error": detalle_error}, status=500
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con microservicio: {str(e)}", exc_info=True)

        if model:
            model.objects.create(
                tipo=tipo,
                **({"identificador": id} if id else {}),
                fecha_especificada=fecha_especificada,
                ip_cliente=get.client_ip(request),
                numero_destino=numero,
                mensaje=mensaje,
                archivo_pdf=payload["image_path"],
                estado="Fallido",
                detalle_error=str(e),
            )

        return JsonResponse(
            {"error": f"Error de conexión con microservicio: {str(e)}"}, status=500
        )
