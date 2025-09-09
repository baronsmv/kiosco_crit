from datetime import date

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import BuscarIdFechaForm
from .models import (
    CitasCarnetWhatsapp,
    CitasCarnetConsulta,
    CitasColaboradorConsulta,
    CitasColaboradorWhatsapp,
)
from .utils import config
from .utils.data import data_queries, exist_queries, handle_data
from .utils.logger import get_logger
from .utils.parsers import buscar, enviar_pdf

logger = get_logger(__name__)

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
            **config.cfg_whatsapp_admin.get("context", {}),
            "qr_data_url": qr_data_url,
            "error_qr": error_qr,
            "status_message": status_message,
            "client_status": client_status,
            "node_base_url": base_url,
        },
    )


def buscar_citas_por_carnet(request):
    return buscar(
        request,
        data=config.cfg_citas_carnet,
        form=BuscarIdFechaForm,
        model=CitasCarnetConsulta,
        exist_func=exist_queries.paciente,
        get_func=handle_data.obtener_datos,
        query_func=data_queries.citas_carnet,
        format_func=handle_data.formatear_datos,
        identificador="carnet",
        persona="paciente",
        objetos="citas",
        pdf_url="pdf_citas_carnet",
    )


@csrf_exempt
def pdf_citas_por_carnet(request, carnet):
    return enviar_pdf(
        request,
        carnet,
        identificador="carnet",
        persona="paciente",
        format_func=handle_data.formatear_datos,
        data=config.cfg_citas_carnet,
        model=CitasCarnetWhatsapp,
    )


def buscar_citas_por_colaborador(request):
    return buscar(
        request,
        data=config.cfg_citas_colaborador,
        form=BuscarIdFechaForm,
        model=CitasColaboradorConsulta,
        exist_func=exist_queries.colaborador,
        get_func=handle_data.obtener_datos,
        query_func=data_queries.citas_colaborador,
        format_func=handle_data.formatear_datos,
        identificador="nombre de usuario",
        persona="colaborador",
        objetos="citas",
        pdf_url="pdf_citas_carnet",
        fecha_inicial=date.today(),
        auto_borrado=False,
    )


@csrf_exempt
def pdf_citas_por_colaborador(request, id):
    return enviar_pdf(
        request,
        id,
        identificador="nombre de usuario",
        persona="colaborador",
        format_func=handle_data.formatear_datos,
        data=config.cfg_citas_colaborador,
        model=CitasColaboradorWhatsapp,
    )
