import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import BuscarPacienteForm
from .models import CitasWhatsapp, CitasConsulta
from .utils.config import whatsapp_admin, citas_web, citas_sql, citas_pdf
from .utils.get_data import formatear_citas, obtener_citas
from .utils.logger import get_logger
from .utils.parsers import buscar, enviar_pdf

logger = get_logger("backend_views")

base_url = settings.WHATSAPP_API_BASE_URL


@login_required
def admin_whatsapp(request):
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
            **whatsapp_admin.get("context", {}),
            "qr_data_url": qr_data_url,
            "error_qr": error_qr,
            "status_message": status_message,
            "client_status": client_status,
            "node_base_url": base_url,
        },
    )


def buscar_citas_paciente(request):
    return buscar(
        request,
        web_data=citas_web,
        sql_data=citas_sql,
        form=BuscarPacienteForm,
        model=CitasConsulta,
        get_func=obtener_citas,
        format_func=formatear_citas,
        identificador="carnet",
        persona="paciente",
        objetos="citas",
    )


@csrf_exempt
def enviar_citas_paciente(request, carnet, fecha):
    return enviar_pdf(
        request,
        id=carnet,
        identificador="carnet",
        persona="paciente",
        pdf_data=citas_pdf,
        sql_data=citas_sql,
        model=CitasWhatsapp,
    )
