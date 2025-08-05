import os

from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from utils.logger import get_logger  # type: ignore
from weasyprint import HTML

from .models import Paciente, EnvioWhatsApp

logger = get_logger("backend_views")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests

base_url = settings.WHATSAPP_API_BASE_URL


@login_required
def admin_whatsapp(request):
    qr_data_url = None
    error_qr = None
    status_message = ""
    client_status = {}

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
        },
    )


def buscar_paciente(request):
    paciente = None
    carnet_proporcionado = False

    if request.method == "POST":
        carnet = request.POST.get("carnet")
        carnet_proporcionado = True
        try:
            paciente = Paciente.objects.get(carnet=carnet)
        except Paciente.DoesNotExist:
            paciente = None

    return render(
        request,
        "pacientes/buscar_paciente.html",
        {
            "header": "Consulta de Paciente",
            "paciente": paciente,
            "carnet_proporcionado": carnet_proporcionado,
        },
    )


@csrf_exempt
def enviar_pdf_whatsapp(request, carnet):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero = request.POST.get("numero")
    if not numero:
        return JsonResponse({"error": "Número de WhatsApp requerido"}, status=400)

    try:
        paciente = Paciente.objects.get(carnet=carnet)
    except Paciente.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

    # 1. Generar el PDF
    filename = f"paciente_{carnet}.pdf"
    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    html = render_to_string("pacientes/pdf_paciente.html", {"paciente": paciente})
    HTML(string=html).write_pdf(output_path)

    # 2. Preparar mensaje
    mensaje = f"""Datos del paciente:
Nombre: {paciente.nombre}
Carnet: {paciente.carnet}
Diagnóstico: {paciente.diagnostico}
Fecha de ingreso: {paciente.fecha_ingreso}"""

    payload = {
        "number": numero + "@c.us",
        "message": mensaje,
        "image_path": f"media/pdfs/{filename}",
    }

    # 3. Enviar al microservicio
    try:
        response = requests.post(f"{base_url}/send-media", json=payload)
        data = response.json()

        estado = "enviado" if response.status_code == 200 else "fallido"
        detalle_error = (
            None if estado == "enviado" else data.get("error", "Error desconocido")
        )

        # Guardar en DB
        EnvioWhatsApp.objects.create(
            paciente=paciente,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado=estado,
            detalle_error=detalle_error,
        )

        if estado == "enviado":
            return JsonResponse({"status": "enviado", "detalles": data})
        else:
            return JsonResponse(
                {"status": "fallido", "error": detalle_error}, status=500
            )

    except requests.exceptions.RequestException as e:
        EnvioWhatsApp.objects.create(
            paciente=paciente,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado="fallido",
            detalle_error=str(e),
        )
        return JsonResponse(
            {"error": f"Error de conexión con microservicio: {str(e)}"}, status=500
        )
