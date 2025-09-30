import hashlib
import os
import re
from datetime import date
from typing import Callable, Dict, Optional, Type

import requests
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.exceptions import ValidationError
from django.db.models import Model
from django.db.utils import OperationalError
from django.forms.forms import Form
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from weasyprint import HTML

from .data import handle_data
from .get_client import ip
from .logger import get_logger

logger = get_logger(__name__)

base_url = settings.WHATSAPP_API_BASE_URL


def menu(request: HttpRequest, config: Dict[str, Dict]) -> HttpResponse:
    menu_options = tuple(
        (
            reverse_lazy(key),
            option.get("title", ""),
            option.get("description", ""),
        )
        for key, option in config.get("options", {}).items()
    )
    return render(
        request,
        "kiosco/menu.html",
        config.get("context", {})
        | {"home_url": reverse_lazy("home"), "menu_options": menu_options},
    )


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


def validar_id(
    input_str: str,
    max_length: int = 50,
    pattern: str = r"^[a-zA-Z0-9. -]+$",
):
    if len(input_str) > max_length:
        raise ValidationError("El ID es demasiado largo.")
    if not re.match(pattern, input_str):
        raise ValidationError("El ID contiene caracteres inválidos.")


def parse_form(
    request: HttpRequest,
    context: Dict,
    campos: Dict,
    sql_campos: Dict,
    form: Form,
    model: Type[Model],
    exist_func: Optional[Callable] = None,
    get_func: Optional[Callable] = None,
    query_func: Callable = None,
    format_func: Callable = None,
    identificador: str = "",
    persona: str = "",
    objetos: str = "",
    pdf_url: str = "",
):
    form_fields = form.fields.keys()

    has_id = "id" in form_fields
    has_fecha = "fecha" in form_fields

    if form.is_valid():
        id = form.cleaned_data.get("id") if has_id else None
        fecha = form.cleaned_data.get("fecha") if has_fecha else None

        if has_id:
            try:
                validar_id(id)
            except ValidationError as e:
                form.add_error("id", e)
                context.update(
                    {
                        "id_error": True,
                        "date_error": has_fecha and bool(form["fecha"].errors),
                    }
                )
                logger.warning(f"Error de validación en ID: {e}")
                model.objects.create(
                    identificador=id,
                    fecha_especificada=fecha,
                    ip_cliente=ip(request),
                    estado="invalido",
                )
                return

        context.update(
            {
                "id": id or "",
                "id_proporcionado": bool(id),
                "fecha": fecha,
                "pdf_url": reverse(
                    pdf_url, args=(id if id else fecha.strftime("%Y-%m-%d"),)
                ),
            }
        )

        resultado = None
        try:
            if has_id:
                resultado = get_func(
                    id=id,
                    sql_campos=sql_campos,
                    exist_func=exist_func,
                    query_func=query_func,
                    fecha=fecha,
                )
            elif has_fecha:
                resultado = query_func(fecha=fecha)
        except OperationalError as e:
            logger.error(f"Error de conexión a la base de datos: {e}")
            model.objects.create(
                identificador=id if id else None,
                fecha_especificada=fecha,
                ip_cliente=ip(request),
                estado="error_conexion",
            )
            context.update(
                {
                    "mensaje_error": "❌ No se pudo conectar con la base de datos.",
                    "id_error": has_id,
                    "date_error": has_fecha,
                    "error_target": "id" if has_id else "fecha",
                }
            )
            return

        if not resultado:
            estado = "inexistente"
        elif not resultado.get("objetos_sf"):
            estado = "no tiene citas"
        else:
            estado = "exitoso"

        formatted = (
            format_func(
                **resultado,
                campos=campos,
                persona=persona,
                identificador=identificador or "fecha",
            )
            if resultado
            else None
        )

        parse_result(
            resultado=resultado,
            context=context,
            fecha=fecha,
            success_dict=formatted,
            identificador=identificador or "fecha",
            persona=persona,
            objetos=objetos,
        )

        request.session["context_data"] = {
            "persona_sf": context.get("persona_sf"),
            "objetos_sf": context.get("objetos_sf"),
            "fecha": (
                context.get("fecha").isoformat()
                if isinstance(context.get("fecha"), date)
                else context.get("fecha")
            ),
        }

        model.objects.create(
            identificador=id if id else None,
            fecha_especificada=fecha,
            ip_cliente=ip(request),
            estado=estado,
        )

    else:
        context.update(
            {
                "id_error": has_id and bool(form["id"].errors),
                "date_error": has_fecha and bool(form["fecha"].errors),
            }
        )
        logger.warning(f"Errores de validación en formulario: {form.errors.as_json()}")


def ajax_buscar(
    request: HttpRequest,
    context: Dict,
    partial: str,
    partial_error: str = "mensaje_error.html",
) -> Optional[HttpResponse]:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = "kiosco/partials/"
        template += partial if context["persona"] else partial_error
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
    return None


def buscar(
    request: HttpRequest,
    data: Dict,
    model: Type[Model],
    form: Type[Form],
    query_func: Callable,
    identificador: Optional[str] = None,
    persona: Optional[str] = None,
    objetos: Optional[str] = None,
    exist_func: Optional[Callable] = None,
    get_func: Callable = handle_data.obtener_datos,
    format_func: Callable = handle_data.formatear_datos,
    pdf_url: Optional[str] = None,
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
        "tipo": "_".join(filter(None, (objetos, persona))),
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
    context["home_url"] = reverse_lazy(context.get("home_url", "home"))
    context["fecha_inicial"] = (
        date.today() if context.get("fecha_inicial", False) else ""
    )

    if request.method == "POST":
        bound_form = form(request.POST)
        has_id = "id" in bound_form.fields

        parse_form(
            request=request,
            context=context,
            campos=web_data.get("campos", {}),
            sql_campos=sql_data.get("campos", {}),
            form=bound_form,
            model=model,
            exist_func=exist_func if has_id else None,
            get_func=get_func if has_id else None,
            query_func=query_func,
            format_func=format_func,
            identificador=identificador,
            persona=persona,
            objetos=objetos,
            pdf_url=(
                pdf_url
                if pdf_url
                else "_".join(filter(None, ("pdf", objetos, persona)))
            ),
        )

        if respuesta_ajax := ajax_buscar(
            request,
            context,
            partial="modal_buscar.html",
        ):
            logger.debug("Respuesta AJAX enviada")
            return respuesta_ajax

    logger.debug("Renderizando vista completa con contexto inicial")
    return render(request, f"kiosco/buscar.html", context)


def generar_pdf(
    format_func: Callable,
    data: Dict[str, Dict],
    previous_context: Dict,
    objetos: str,
    id: Optional[str] = None,
    persona: Optional[str] = None,
    identificador: Optional[str] = None,
    color: bool = False,
) -> str:
    pdf_data = data["pdf"]
    sql_data = data["sql"]

    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)

    if not previous_context:
        logger.error("previous_context está vacío. No se puede generar PDF.")
        raise ValueError("No hay datos de contexto en sesión.")

    logger.debug(f"Contexto recibido en generar_pdf: {previous_context.keys()}")

    fecha_especificada = previous_context.pop("fecha", None)

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
    filename = (
        "_".join(filter(None, (objetos, persona, id, fecha_especificada, content_hash)))
        + ".pdf"
    )
    output_path = os.path.join(output_dir, filename)
    logger.debug(f"Generando PDF en: {output_path}")

    # Buscar CSS
    css_path = finders.find(f"kiosco/css/pdf{'-color' if color else ''}.css")
    css_files = [css_path] if css_path else []

    try:
        HTML(string=html).write_pdf(output_path, stylesheets=css_files)
        logger.debug("PDF generado correctamente")
    except Exception:
        logger.exception("Error al generar el PDF")
        raise

    if not os.path.exists(output_path):
        logger.error(f"El archivo PDF no fue creado: {output_path}")
        raise FileNotFoundError("No se pudo generar el archivo PDF.")

    return filename


def enviar_pdf(
    request: HttpRequest,
    objetos: str,
    data: Dict,
    model: Type[Model],
    id: Optional[str] = None,
    identificador: Optional[str] = None,
    persona: Optional[str] = None,
    format_func: Callable = handle_data.formatear_datos,
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
    fecha_especificada = web_context.get("fecha", None)

    filename = generar_pdf(
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
            fecha_especificada=fecha_especificada,
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
