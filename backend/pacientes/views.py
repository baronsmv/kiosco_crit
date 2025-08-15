import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from utils.get_data import formatear_citas, obtener_citas  # type: ignore
from utils.logger import get_logger  # type: ignore
from weasyprint import HTML

from .forms import BuscarPacienteForm
from .models import EnvioWhatsApp

logger = get_logger("backend_views")

from django.contrib.auth.decorators import login_required
import requests

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
            "title": "Administración de WhatsApp",
            "header": "Administración de WhatsApp",
            "qr_data_url": qr_data_url,
            "error_qr": error_qr,
            "status_message": status_message,
            "client_status": client_status,
            "node_base_url": settings.WHATSAPP_API_BASE_URL,
        },
    )


def buscar_paciente(request):
    logger.debug(f"Request method: {request.method}")
    print("POST data:", request.POST, flush=True)

    context = {
        "title": "Búsqueda de citas",
        "header": "Búsqueda de citas",
        "form_label": "Número de Carnet:",
        "form_placeholder": "Ej: 123456",
        "button_label": "Buscar",
        "date_placeholder": "Ej: 01-01-25",
        "date_label": "Fecha:",
        "send_button_label": "📤 Enviar por WhatsApp",
        "form_error": False,
        "date_error": False,
        "carnet": "",
        "carnet_proporcionado": False,
        "paciente": None,
        "tabla_titulo": "Citas",
        "tabla_columnas": ("Servicio", "Fecha", "Colaborador"),
        "mensaje_error": "",
        "error_target": "",
    }

    if request.method == "POST":
        form = BuscarPacienteForm(request.POST)

        if form.is_valid():
            carnet = form.cleaned_data["carnet"]
            fecha = form.cleaned_data["fecha"]
            context.update(
                {
                    "carnet": carnet,
                    "carnet_proporcionado": True,
                    "fecha": fecha,
                }
            )

            resultado = obtener_citas(carnet, fecha)

            if resultado is None or resultado.get("error") == "paciente_no_encontrado":
                context.update(
                    {
                        "form_error": True,
                        "error_target": "carnet",
                        "mensaje_error": "❌ No se encontró ningún paciente con ese carnet.",
                    }
                )
                logger.warning(context["mensaje_error"])

            elif not resultado["citas"]:
                error_context = {
                    "mensaje_error": (
                        "❌ No se encontraron citas con la fecha especificada."
                        if fecha
                        else "❌ No se encontraron citas para este carnet."
                    ),
                    "error_target": "fecha" if fecha else "carnet",
                }

                context.update(error_context)
                context[error_context["error_target"] + "_error"] = True
                logger.info(error_context["mensaje_error"])

            else:
                paciente_fmt, citas_fmt = formatear_citas(
                    resultado["paciente"], resultado["citas"]
                )
                context.update(
                    {
                        "paciente": paciente_fmt,
                        "tabla": citas_fmt,
                    }
                )
        else:
            context.update(
                {
                    "form_error": bool(form["carnet"].errors),
                    "date_error": bool(form["fecha"].errors),
                }
            )
            logger.warning("Formulario inválido")

        # Respuesta AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            template = (
                "pacientes/partials/modal_paciente.html"
                if context["paciente"]
                else "pacientes/partials/mensaje_error.html"
            )
            html = render_to_string(template, context, request=request)
            return HttpResponse(html)

    return render(request, "pacientes/buscar_paciente.html", context)


@csrf_exempt
def enviar_pdf_whatsapp(request, carnet):
    logger.debug(
        f"enviar_pdf_whatsapp called with method {request.method} and carnet {carnet}"
    )

    if request.method != "POST":
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({"error": "Método no permitido"}, status=405)

    numero = request.POST.get("numero")
    logger.debug(f"Numero recibido: {numero}")
    if not numero:
        logger.error("Número de WhatsApp requerido no proporcionado")
        return JsonResponse({"error": "Número de WhatsApp requerido"}, status=400)

    resultado = obtener_citas(carnet)

    if resultado is None or resultado.get("error") == "paciente_no_encontrado":
        logger.error(f"Paciente no encontrado con carnet {carnet}")
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

    paciente, citas = formatear_citas(resultado["paciente"], resultado["citas"])
    logger.debug(f"Paciente obtenido: {paciente}")
    logger.debug(f"Citas obtenidas: {citas}")

    # Generar PDF
    filename = f"paciente_{carnet}.pdf"
    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    logger.debug(f"Generando PDF en: {output_path}")

    css_path = finders.find("pacientes/css/pdf_paciente.css")
    css_files = [css_path] if css_path else []

    html = render_to_string(
        "pacientes/pdf_paciente.html",
        {
            "paciente": paciente,
            "tabla": citas,
            "tabla_titulo": "Citas",
            "tabla_columnas": ("Servicio", "Fecha", "Colaborador"),
        },
    )
    HTML(string=html).write_pdf(output_path, stylesheets=css_files)
    logger.debug("PDF generado correctamente")

    # Mensaje WhatsApp
    mensaje = f"""Datos del paciente:
Nombre: {paciente['Nombre']}
Carnet: {paciente['Carnet']}
Cantidad de citas: {len(citas)}"""

    payload = {
        "number": numero + "@c.us",
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

        EnvioWhatsApp.objects.create(
            carnet=carnet,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado=estado,
            detalle_error=detalle_error,
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
        EnvioWhatsApp.objects.create(
            carnet=carnet,
            numero_destino=numero,
            mensaje=mensaje,
            archivo_pdf=payload["image_path"],
            estado="fallido",
            detalle_error=str(e),
        )
        return JsonResponse(
            {"error": f"Error de conexión con microservicio: {str(e)}"}, status=500
        )
