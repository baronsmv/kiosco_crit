from datetime import date
from typing import Dict, Optional, Type, Callable

from django.db import OperationalError
from django.forms import Form
from django.http import HttpRequest

from . import get, validate
from .exceptions import AjaxException
from .logger import get_logger
from .. import models

logger = get_logger(__name__)


def form(
    request: HttpRequest,
    context: Dict,
    config_data: Dict,
    form: Form,
    model: Optional[Type[models.Base]],
    exist_query: Optional[Callable],
    data_query: Callable,
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

    if not form.is_valid():
        context.update(
            {
                "id_error": has_id and bool(form["id"].errors),
                "date_error": has_fecha and bool(form["fecha"].errors),
            }
        )
        logger.warning(f"Errores de validación en formulario: {form.errors.as_json()}")
        return

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

    context.update({"id": id or "", "fecha": fecha})

    try:
        sujeto = get.subject(
            id,
            exist_query=exist_query,
            nombre_sujeto=nombre_sujeto,
            nombre_id=nombre_id,
        )
        objetos = get.all_objects(
            id,
            fecha,
            data_query=data_query,
            nombre_objetos=nombre_objetos,
            nombre_id=nombre_id,
        )
    except OperationalError as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        if model:
            model.objects.create(
                tipo=tipo,
                identificador=id if has_id else None,
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado="Error de conexión",
            )
        raise AjaxException("❌ No se pudo conectar con la base de datos.")
    except AjaxException as e:
        if model:
            model.objects.create(
                tipo=tipo,
                identificador=id if has_id else None,
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado=e.causa,
            )
        raise

    context["sujeto"] = sujeto
    context["tabla"] = get.filtered_objects(
        objetos, campos=web_campos, sql_campos=sql_campos
    )

    if model:
        model.objects.create(
            tipo=tipo,
            **({"identificador": id} if has_id else {}),
            fecha_especificada=fecha,
            ip_cliente=ip_cliente,
            estado="Exitoso",
        )

    request.session["context_data"] = {
        "sujeto": sujeto,
        "tabla": context.get("tabla"),
        "id": id or "",
        "fecha": (fecha.isoformat() if isinstance(fecha, date) else fecha),
        "nombre_objetos": nombre_objetos,
        "nombre_sujeto": nombre_sujeto,
        "nombre_id": nombre_id,
        "pdf_data": pdf_data,
        "sql_data": sql_data,
    }
