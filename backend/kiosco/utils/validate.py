import re
from datetime import date
from typing import Callable, Dict, Optional, Type

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.db.utils import OperationalError
from django.forms.forms import Form
from django.http import HttpRequest
from django.urls import reverse

from . import get
from .logger import get_logger

logger = get_logger(__name__)


def _add_result(
    resultado: Dict,
    context: Dict,
    fecha: Optional,
    success_dict: Dict,
    identificador: str,
    persona: str,
    objetos: str,
) -> None:
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

    else:
        context.update(**success_dict, **resultado)
        logger.info(
            f"{len(resultado.get('objetos_sf', []))} {objetos} encontrados para {persona} con ID {identificador}"
        )


def _validate_id(id: str, max_length: int, pattern: str) -> None:
    if len(id) > max_length:
        raise ValidationError("El ID es demasiado largo.")
    if not re.match(pattern, id):
        raise ValidationError("El ID contiene caracteres inválidos.")


def form(
    request: HttpRequest,
    context: Dict,
    campos: Dict,
    sql_campos: Dict,
    form: Form,
    model: Type[Model],
    exist_func: Optional[Callable],
    get_func: Callable,
    query_func: Callable,
    format_func: Callable,
    identificador: str = "",
    persona: str = "",
    objetos: str = "",
    pdf_url: str = "",
) -> None:
    form_fields = form.fields.keys()

    has_id = "id" in form_fields
    has_fecha = "fecha" in form_fields

    if form.is_valid():
        id = form.cleaned_data["id"] if has_id else None
        fecha = form.cleaned_data["fecha"] if has_fecha else None

        if has_id:
            try:
                _validate_id(
                    id=id,
                    max_length=context.get("id_max_length", 20),
                    pattern=context.get("id_pattern", r"^[a-zA-Z0-9. \-]+$"),
                )
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
                    ip_cliente=get.client_ip(request),
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

        try:
            resultado = get_func(
                id=id,
                fecha=fecha,
                sql_campos=sql_campos,
                exist_func=exist_func if has_id else None,
                query_func=query_func,
            )
        except OperationalError as e:
            logger.error(f"Error de conexión a la base de datos: {e}")
            model.objects.create(
                identificador=id if id else None,
                fecha_especificada=fecha,
                ip_cliente=get.client_ip(request),
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

        _add_result(
            resultado=resultado,
            context=context,
            fecha=fecha,
            success_dict=formatted,
            identificador=identificador or "fecha",
            persona=persona,
            objetos=objetos,
        )

        fecha_context = context.get("fecha")
        request.session["context_data"] = {
            "persona_sf": context.get("persona_sf"),
            "objetos_sf": context.get("objetos_sf"),
            "fecha": (
                fecha_context.isoformat()
                if isinstance(fecha_context, date)
                else fecha_context
            ),
        }

        model.objects.create(
            identificador=id if id else None,
            fecha_especificada=fecha,
            ip_cliente=get.client_ip(request),
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
