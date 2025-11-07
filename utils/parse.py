from datetime import date
from typing import Callable, Dict, Tuple, Optional, Type

from django.db import OperationalError
from django.forms import Form
from django.http import HttpRequest

from classes import models
from classes.exceptions import AjaxException
from utils import get, validate
from utils.logger import get_logger

logger = get_logger(__name__)


def query(
    query: str,
    id: Optional[str] = None,
    fecha: Optional[date] = None,
    *,
    filters: Optional[Dict] = None,
    order_by: Optional[str] = None,
    fecha_query: str = " AND CAST(kc.FE_CITA AS DATE) = %s",
) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Generando consulta para ID: {id} con fecha: {fecha}")
    params = tuple(filter(None, (id, fecha)))

    if fecha:
        query += fecha_query
        logger.debug("Agregado filtro adicional por fecha exacta.")

    if filters:
        for k, v in filters.items():
            if fecha:
                valores = v.get("con_fecha")
            else:
                valores = v.get("sin_fecha")
            if valores:
                query += f" AND {k} IN ('" + "', '".join(valores) + "')"

    if order_by:
        query += f" ORDER BY {order_by}"

    logger.debug(f"Query final generado: {query}")
    logger.debug(f"Parámetros: {params}")

    return query, params


def form(
    request: HttpRequest,
    context: Dict,
    config_data: Dict,
    form: Form,
    model: Optional[Type[models.BaseModel]],
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
    tipo = get.model_type(nombre_objetos=nombre_objetos, nombre_sujeto=nombre_sujeto)

    web_data = config_data["web"]
    pdf_data = config_data["pdf"]
    sql_data = config_data["sql"]

    if not form.is_valid():
        logger.warning(f"Errores de validación en formulario: {form.errors.as_json()}")
        raise AjaxException()

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
        raise AjaxException(f"{nombre_id.capitalize()} no válido.")

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
        objetos,
        campos=web_data.get("campos", {}),
        sql_campos=sql_data.get("campos", {}),
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
        "objetos": objetos,
        "id": id or "",
        "fecha": (fecha.isoformat() if isinstance(fecha, date) else fecha),
        "nombre_objetos": nombre_objetos,
        "nombre_sujeto": nombre_sujeto,
        "nombre_id": nombre_id,
        "pdf_data": pdf_data,
        "sql_data": sql_data,
    }
