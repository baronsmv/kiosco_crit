import re
from typing import Dict, Type, Optional, Callable

import requests
from django.conf import settings
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .. import models
from ..utils import config, format, generate, get
from ..utils.logger import get_logger

logger = get_logger(__name__)

base_url = settings.WHATSAPP_API_BASE_URL


def _send_pdf(
    request: HttpRequest,
    objetos: str,
    data: Dict,
    model: Type[Model],
    id: Optional[str] = None,
    identificador: Optional[str] = None,
    persona: Optional[str] = None,
    format_func: Callable = format.campos,
) -> JsonResponse:
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
    fecha_especificada = web_context.get("fecha", None)

    filename = generate.pdf(
        id=id,
        format_func=format_func,
        data=data,
        previous_context=web_context,
        persona=persona,
        identificador=identificador,
        objetos=objetos,
        color=True,
    )

    # Mensaje WhatsApp
    mensaje = f"""Datos del {persona}:
Nombre: {web_context['persona']['Nombre']}
{identificador.title()}: {web_context['persona'][identificador.title()]}"""

    payload = {
        "number": "521" + re.sub(r"\D", "", numero) + "@c.us",
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


@csrf_exempt
def citas_paciente(request: HttpRequest, carnet: str) -> HttpResponse:
    return _send_pdf(
        request=request,
        id=carnet,
        identificador="carnet",
        persona="paciente",
        objetos="citas",
        data=config.cfg_citas_paciente,
        model=models.CitasCarnetWhatsapp,
    )


@csrf_exempt
def citas_colaborador(request: HttpRequest, id: str) -> HttpResponse:
    return _send_pdf(
        request=request,
        id=id,
        identificador="nombre de usuario",
        persona="colaborador",
        objetos="citas",
        data=config.cfg_citas_colaborador,
        model=models.CitasColaboradorWhatsapp,
    )


@csrf_exempt
def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return _send_pdf(
        request=request,
        data=config.cfg_espacios,
        model=models.EspaciosVaciosWhatsapp,
        objetos="espacios",
    )
