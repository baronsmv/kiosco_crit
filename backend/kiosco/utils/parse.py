from datetime import date
from typing import Dict, Optional, Type, Callable

from django.db import OperationalError
from django.forms import Form
from django.http import HttpRequest

from . import get, validate
from .logger import get_logger
from .. import models

logger = get_logger(__name__)


def form_result(
    resultado: Dict,
    context: Dict,
    fecha: Optional,
    success_dict: Dict,
    nombre_id: str,
    nombre_sujeto: str,
    nombre_objetos: str,
) -> None:
    if not resultado:
        context.update(
            {
                "id_error": True,
                "error_target": "id",
                "mensaje_ajax": f"❌ No se encontró ningún {nombre_sujeto} con ese {nombre_id}.",
                "tipo_ajax": "error",
            }
        )
        logger.warning(f"ID inválido: {nombre_id} - No se encontró {nombre_sujeto}")

    elif not resultado.get(f"objetos_sf"):
        error_context = {
            "mensaje_ajax": (
                f"❌ No se encontraron {nombre_objetos} con la fecha especificada."
                if fecha
                else f"❌ No se encontraron {nombre_objetos} activas para este {nombre_id}."
            ),
            "tipo_ajax": "error",
            "error_target": "fecha" if fecha else "id",
        }
        context.update(error_context)
        context[error_context["error_target"] + "_error"] = True
        logger.info(f"Sin resultados para {nombre_objetos} con ID {nombre_id}")

    else:
        context.update(**success_dict, **resultado)
        logger.info(
            f"{len(resultado.get('objetos_sf', []))} {nombre_objetos} encontrados para {nombre_sujeto} con ID {nombre_id}"
        )


def form(
    request: HttpRequest,
    context: Dict,
    config_data: Dict,
    form: Form,
    model: Optional[Type[models.Base]],
    exist_query: Optional[Callable],
    data_query: Callable,
    get_func: Callable,
    format_func: Callable,
    nombre_id: str = "",
    nombre_sujeto: str = "",
    nombre_objetos: str = "",
) -> None:
    form_fields = form.fields.keys()
    has_id = "id" in form_fields
    has_fecha = "fecha" in form_fields

    ip_cliente = get.client_ip(request)

    web_data = config_data["web"]
    pdf_data = config_data["pdf"]
    sql_data = config_data["sql"]

    web_campos = web_data.get("campos", {})
    sql_campos = sql_data.get("campos", {})

    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    if form.is_valid():
        id = form.cleaned_data["id"] if has_id else None
        fecha = form.cleaned_data["fecha"] if has_fecha else None

        if has_id and not validate.id(
            id=id,
            fecha=fecha,
            has_fecha=has_fecha,
            context=context,
            model=model,
            reg_form=form,
            ip_cliente=ip_cliente,
            tipo=tipo,
        ):
            return

        context.update(
            {
                "id": id or "",
                "id_proporcionado": bool(id),
                "fecha": fecha,
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
            if model:
                model.objects.create(
                    tipo=tipo,
                    **({"identificador": id} if has_id else {}),
                    fecha_especificada=fecha,
                    ip_cliente=ip_cliente,
                    estado="Error de conexión",
                )
            context.update(
                {
                    "mensaje_ajax": "❌ No se pudo conectar con la base de datos.",
                    "tipo_ajax": "error",
                    "id_error": has_id,
                    "date_error": has_fecha,
                    "error_target": "id" if has_id else "fecha",
                }
            )
            return

        if not resultado:
            estado = "ID Inexistente"
        elif not resultado.get("objetos_sf"):
            estado = f"Sin {nombre_objetos.lower()}"
        else:
            estado = "Exitoso"

        formatted = (
            format_func(
                **resultado,
                campos=web_campos,
                nombre_sujeto=nombre_sujeto,
                nombre_id=nombre_id,
            )
            if resultado
            else None
        )

        form_result(
            resultado=resultado,
            context=context,
            fecha=fecha,
            success_dict=formatted,
            nombre_id=nombre_id,
            nombre_sujeto=nombre_sujeto,
            nombre_objetos=nombre_objetos,
        )

        fecha_context = context.get("fecha")
        request.session["context_data"] = {
            "sujeto": context.get("sujeto"),
            "tabla": context.get("tabla"),
            "id": id or "",
            "fecha": (
                fecha_context.isoformat()
                if isinstance(fecha_context, date)
                else fecha_context
            ),
            "nombre_objetos": nombre_objetos,
            "nombre_sujeto": nombre_sujeto,
            "nombre_id": nombre_id,
            "pdf_data": pdf_data,
            "sql_data": sql_data,
        }

        if model:
            model.objects.create(
                tipo=tipo,
                **({"identificador": id} if has_id else {}),
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
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
