import re
from datetime import date, datetime
from typing import Callable, Dict, Optional, Type

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.db.utils import OperationalError
from django.forms.forms import Form
from django.http import HttpRequest
from django.urls import reverse_lazy

from . import get
from .logger import get_logger

logger = get_logger(__name__)


def _check_id_pattern(id: str, max_length: int, pattern: str) -> None:
    if len(id) > max_length:
        raise ValidationError("El ID es demasiado largo.")
    if not re.match(pattern, id):
        raise ValidationError("El ID contiene caracteres inválidos.")


def _valid_id(
    id: str,
    fecha: datetime,
    has_fecha: bool,
    context: Dict,
    RegModel: Optional[Type[Model]],
    reg_form: Form,
    ip_cliente: str,
) -> bool:
    try:
        _check_id_pattern(
            id=id,
            max_length=context.get("id_max_length", 20),
            pattern=context.get("id_pattern", r"^[a-zA-Z0-9. \-]+$"),
        )
        return True
    except ValidationError as e:
        reg_form.add_error("id", e)
        context.update(
            {
                "id_error": True,
                "date_error": has_fecha and bool(reg_form["fecha"].errors),
            }
        )
        logger.warning(f"Error de validación en ID: {e}")
        if RegModel:
            RegModel.objects.create(
                identificador=id,
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado="invalido",
            )
        return False


def _add_result(
    resultado: Dict,
    context: Dict,
    fecha: Optional,
    success_dict: Dict,
    nombre_id: str,
    nombre_persona: str,
    nombre_objetos: str,
) -> None:
    if not resultado:
        context.update(
            {
                "id_error": True,
                "error_target": "id",
                "mensaje_error": f"❌ No se encontró ningún {nombre_persona} con ese {nombre_id}.",
            }
        )
        logger.warning(f"ID inválido: {nombre_id} - No se encontró {nombre_persona}")

    elif not resultado.get(f"objetos_sf"):
        error_context = {
            "mensaje_error": (
                f"❌ No se encontraron {nombre_objetos} con la fecha especificada."
                if fecha
                else f"❌ No se encontraron {nombre_objetos} activas para este {nombre_id}."
            ),
            "error_target": "fecha" if fecha else "id",
        }
        context.update(error_context)
        context[error_context["error_target"] + "_error"] = True
        logger.info(f"Sin resultados para {nombre_objetos} con ID {nombre_id}")

    else:
        context.update(**success_dict, **resultado)
        logger.info(
            f"{len(resultado.get('objetos_sf', []))} {nombre_objetos} encontrados para {nombre_persona} con ID {nombre_id}"
        )


def form(
    request: HttpRequest,
    context: Dict,
    config_data: Dict,
    reg_form: Form,
    RegModel: Optional[Type[Model]],
    exist_query: Optional[Callable],
    data_query: Callable,
    get_func: Callable,
    format_func: Callable,
    urls: Dict,
    nombre_id: str = "",
    nombre_persona: str = "",
    nombre_objetos: str = "",
) -> None:
    form_fields = reg_form.fields.keys()
    has_id = "id" in form_fields
    has_fecha = "fecha" in form_fields

    ip_cliente = get.client_ip(request)

    web_data = config_data["web"]
    pdf_data = config_data["pdf"]
    sql_data = config_data["sql"]

    web_campos = web_data.get("campos", {})
    sql_campos = sql_data.get("campos", {})

    if reg_form.is_valid():
        id = reg_form.cleaned_data["id"] if has_id else None
        fecha = reg_form.cleaned_data["fecha"] if has_fecha else None

        if has_id and not _valid_id(
            id=id,
            fecha=fecha,
            has_fecha=has_fecha,
            context=context,
            RegModel=RegModel,
            reg_form=reg_form,
            ip_cliente=ip_cliente,
        ):
            return

        context.update(
            {
                "id": id or "",
                "id_proporcionado": bool(id),
                "fecha": fecha,
                **{name: reverse_lazy(url) for name, url in urls.items()},
            }
        )

        try:
            resultado = get_func(
                id=id,
                fecha=fecha,
                sql_campos=sql_campos,
                exist_query=exist_query if has_id else None,
                data_query=data_query,
            )
        except OperationalError as e:
            logger.error(f"Error de conexión a la base de datos: {e}")
            if RegModel:
                RegModel.objects.create(
                    **({"identificador": id} if has_id else {}),
                    fecha_especificada=fecha,
                    ip_cliente=ip_cliente,
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
                campos=web_campos,
                nombre_persona=nombre_persona,
                nombre_id=nombre_id,
            )
            if resultado
            else None
        )

        _add_result(
            resultado=resultado,
            context=context,
            fecha=fecha,
            success_dict=formatted,
            nombre_id=nombre_id,
            nombre_persona=nombre_persona,
            nombre_objetos=nombre_objetos,
        )

        fecha_context = context.get("fecha")
        request.session["context_data"] = {
            "persona_sf": context.get("persona_sf"),
            "objetos_sf": context.get("objetos_sf"),
            "id": id or "",
            "fecha": (
                fecha_context.isoformat()
                if isinstance(fecha_context, date)
                else fecha_context
            ),
            "nombre_objetos": nombre_objetos,
            "nombre_persona": nombre_persona,
            "nombre_id": nombre_id,
            "pdf_data": pdf_data,
            "sql_data": sql_data,
        }

        if RegModel:
            RegModel.objects.create(
                **({"identificador": id} if has_id else {}),
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado=estado,
            )

    else:
        context.update(
            {
                "id_error": has_id and bool(reg_form["id"].errors),
                "date_error": has_fecha and bool(reg_form["fecha"].errors),
            }
        )
        logger.warning(
            f"Errores de validación en formulario: {reg_form.errors.as_json()}"
        )
