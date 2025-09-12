from datetime import date

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
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
from .utils.parsers import buscar, enviar_pdf, generar_pdf

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


def home(request):
    menu_options = tuple(
        (
            reverse_lazy(key),
            option.get("title", ""),
            option.get("description", ""),
        )
        for key, option in config.cfg_home.get("options", {}).items()
    )
    return render(
        request,
        "kiosco/home.html",
        config.cfg_home.get("context", {}) | {"menu_options": menu_options},
    )


def vista_previa_pdf(request, tipo, id):
    abrir = request.GET.get("abrir") == "1"

    if tipo == "citas_colaborador":
        persona = "colaborador"
        objetos = "citas"
        identificador = "nombre de usuario"
        data = config.cfg_citas_colaborador
    elif tipo == "citas_paciente":
        persona = "paciente"
        objetos = "citas"
        identificador = "carnet"
        data = config.cfg_citas_carnet
    else:
        return JsonResponse({"error": "Tipo inválido"}, status=400)

    filename = generar_pdf(
        id=id,
        format_func=handle_data.formatear_datos,
        data=data,
        previous_context=request.session.get("context_data", {}),
        identificador=identificador,
        persona=persona,
        objetos=objetos,
    )

    file_url = f"/media/pdfs/{filename}"

    if abrir:
        return HttpResponseRedirect(file_url)

    iframe_html = f"""
    <div style="height: 60vh; margin-top: 2rem; padding: 1rem;">
        <iframe src="{file_url}" width="100%" height="100%" style="border: none; border-radius: 8px;"></iframe>
    </div>
    """
    return JsonResponse({"html": iframe_html, "filename": filename})


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
        fecha_inicial=None,
        auto_borrado=True,
        mostrar_imprimir=True,
        mostrar_inicio=True,
    )


@csrf_exempt
def pdf_citas_por_carnet(request, carnet):
    return enviar_pdf(
        request,
        carnet,
        identificador="carnet",
        persona="paciente",
        objetos="citas",
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
        mostrar_imprimir=True,
        mostrar_inicio=True,
    )


@csrf_exempt
def pdf_citas_por_colaborador(request, id):
    return enviar_pdf(
        request,
        id,
        identificador="nombre de usuario",
        persona="colaborador",
        objetos="citas",
        format_func=handle_data.formatear_datos,
        data=config.cfg_citas_colaborador,
        model=CitasColaboradorWhatsapp,
    )
