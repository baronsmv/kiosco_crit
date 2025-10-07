from typing import Type, Callable, Optional

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import Model
from django.http import HttpRequest, JsonResponse

from ..utils import format, generate, get
from ..utils.logger import get_logger

logger = get_logger(__name__)

base_url = settings.WHATSAPP_API_BASE_URL


def pdf_email(
    request: HttpRequest,
    RegModel: Optional[Type[Model]] = None,
    format_func: Callable = format.campos,
) -> JsonResponse:
    previous_context = request.session.get("context_data", {})
    id = previous_context.get("id", "")
    nombre_persona = previous_context.get("nombre_persona", "")
    fecha_especificada = previous_context.get("fecha")

    if request.method != "POST":
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    correo = request.POST.get("email")
    logger.debug(f"Email recibido: {correo}")
    try:
        validate_email(correo)
    except ValidationError:
        logger.error("Email inválido")
        return JsonResponse({"error": "Email inválido"}, status=400)

    filename = generate.pdf(
        format_func=format_func,
        previous_context=previous_context,
        salida_a_color=True,
    )
    subject = f"Datos del {nombre_persona}"
    body = "Adjuntamos el archivo solicitado en formato PDF."
    pdf_path = f"media/pdfs/{filename}"

    try:
        email = EmailMessage(subject, body, to=[correo])
        email.attach_file(pdf_path)
        email.send()
    except Exception as e:
        logger.exception("Error enviando correo")
        if RegModel:
            RegModel.objects.create(
                **({"identificador": id} if id else {}),
                email_destino=correo,
                archivo_pdf=pdf_path,
                estado="fallido",
                detalle_error=str(e),
            )
        return JsonResponse({"error": str(e)}, status=500)

    if RegModel:
        RegModel.objects.create(
            **({"identificador": id} if id else {}),
            fecha_especificada=fecha_especificada,
            email_destino=correo,
            archivo_pdf=pdf_path,
            estado="enviado",
            ip_cliente=get.client_ip(request),
        )
    return JsonResponse({"status": "enviado"})


def pdf_whatsapp(
    request: HttpRequest,
    RegModel: Optional[Type[Model]] = None,
    format_func: Callable = format.campos,
) -> JsonResponse:
    previous_context = request.session.get("context_data", {})
    id = previous_context.get("id", "")
    persona = previous_context.get("persona", {})
    nombre_id = previous_context.get("nombre_id")
    nombre_persona = previous_context.get("nombre_persona")
    fecha_especificada = previous_context.get("fecha", None)

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

    filename = generate.pdf(
        format_func=format_func,
        previous_context=previous_context,
        salida_a_color=True,
    )
    mensaje = f"""Datos del {nombre_persona}:
Nombre: {persona['Nombre']}
{nombre_id.title()}: {persona[nombre_id.title()]}"""
    payload = get.whatsapp_payload(number=numero, mensaje=mensaje, filename=filename)

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

        if RegModel:
            RegModel.objects.create(
                **({"identificador": id} if id else {}),
                fecha_especificada=fecha_especificada,
                numero_destino=numero,
                mensaje=mensaje,
                archivo_pdf=payload["image_path"],
                estado=estado,
                detalle_error=detalle_error,
                ip_cliente=get.client_ip(request),
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

        if RegModel:
            RegModel.objects.create(
                **({"identificador": id} if id else {}),
                numero_destino=numero,
                mensaje=mensaje,
                archivo_pdf=payload["image_path"],
                estado="fallido",
                detalle_error=str(e),
            )

        return JsonResponse(
            {"error": f"Error de conexión con microservicio: {str(e)}"}, status=500
        )
