import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from utils import generate
from utils.logger import get_logger
from .utils import whatsapp_pdf_view, email_view

logger = get_logger(__name__)

base_url = settings.WHATSAPP_API_BASE_URL


def email_pdf(request: HttpRequest) -> HttpResponse | JsonResponse:
    previous_context = request.session.get("context_data", {})

    subject = "Datos solitados, CRIT Hidalgo"
    body = "Adjuntamos el archivo solicitado en formato PDF."

    filename = generate.pdf(previous_context, color=True)
    filepath = f"media/pdf/{filename}"

    return email_view(request, filepath, subject, body)


def email_excel(request: HttpRequest) -> HttpResponse | JsonResponse:
    previous_context = request.session.get("context_data", {})

    subject = "Datos solitados, CRIT Hidalgo"
    body = "Adjuntamos el archivo solicitado en formato Excel."

    filename = generate.excel(previous_context)
    filepath = f"media/excel/{filename}"

    return email_view(request, filepath, subject, body)


def email(request: HttpRequest) -> HttpResponse | JsonResponse:
    email = request.POST.get("email")
    format_type = request.POST.get("format")
    logger.info(f"Enviando archivo de tipo '{format_type}' a '{email}'.")

    if format_type == "pdf":
        return email_pdf(request)
    else:
        return email_excel(request)


@csrf_exempt
def whatsapp_pdf(request: HttpRequest) -> HttpResponse | JsonResponse:
    return whatsapp_pdf_view(request)


def whatsapp(request: HttpRequest) -> HttpResponse | JsonResponse:
    format_type = request.POST.get("format")
    if format_type == "pdf":
        return whatsapp_pdf(request)
    else:
        return whatsapp_pdf(request)  # Excel no implementado


@login_required
def whatsapp_admin(request: HttpRequest):
    qr_data_url = None
    error_qr = None
    status_message = ""

    if request.method == "POST":
        if "reset" in request.POST:
            try:
                resp = requests.post(f"{base_url}/reset-clean")
                if resp.status_code == 200:
                    status_message = "🔄 Cliente reiniciado correctamente."
                else:
                    status_message = "❌ Error al reiniciar cliente."
            except Exception as e:
                status_message = f"❌ Error de conexión: {str(e)}"

    # Obtener estado actual
    try:
        status_resp = requests.get(f"{base_url}/status")
        client_status = status_resp.json()
    except Exception as e:
        client_status = {"status": "desconocido", "connected": False}
        status_message += f"\n⚠️ No se pudo obtener el estado: {str(e)}"

    # Obtener QR si disponible
    try:
        qr_resp = requests.get(f"{base_url}/qr")
        qr_json = qr_resp.json()
        qr_data_url = qr_json.get("qr", None)
    except Exception as e:
        error_qr = f"No se pudo obtener el QR: {str(e)}"

    return render(
        request,
        "admin/whatsapp_admin.html",
        {
            "title": "Administración de WhatsApp",
            "header": "Administración de WhatsApp",
            "qr_data_url": qr_data_url,
            "error_qr": error_qr,
            "status_message": status_message,
            "client_status": client_status,
            "node_base_url": base_url,
        },
    )
