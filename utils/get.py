import hashlib
import inspect
import os
import re
from datetime import date
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from django.conf import settings
from django.db import connections, OperationalError
from django.http import HttpRequest
from django.urls import reverse_lazy

from classes.exceptions import AjaxException
from . import map
from .logger import get_logger

logger = get_logger(__name__)
base_url = settings.WHATSAPP_API_BASE_URL


def whatsapp_status(url: str = f"{base_url}/status") -> Dict:
    try:
        return requests.get(url).json()
    except Exception:
        return {"status": "desconocido", "connected": False}


def initial_context(config_data: Dict) -> Dict:
    web_data = config_data["web"]
    context_data = web_data["context"]

    home_url = reverse_lazy(context_data["main"].get("home", {}).get("url", "home"))
    initial_date = (
        date.today() if context_data["main"].get("date", {}).get("initial") else ""
    )

    return {
        **context_data,
        "home_url": home_url,
        "initial_date": initial_date,
        "whatsapp_status": whatsapp_status(),
        "tabla_columnas": map.columns(web_data, sql_data=config_data["sql"]),
        "id": "",
        "sujeto": None,
        "tabla": (),
        "id_proporcionado": False,
        "id_error": False,
        "date_error": False,
        "mensaje_ajax": "",
        "error_target": "",
    }


def sql_selection(sql_config: Dict[str, Dict]) -> str:
    campos = sql_config.get("campos", {})
    seleccion = ", ".join(campos[c]["sql"] + f" AS {c}" for c in campos.keys())
    logger.info(f"Campos seleccionados para query: {seleccion}")
    return seleccion


def model_type(nombre_objetos: str, nombre_sujeto: str) -> str:
    tipo = nombre_objetos.title()
    if nombre_sujeto:
        tipo += f" de {nombre_sujeto.title()}"
    return tipo


def client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")
    return ip


def evaluate_query(func: Callable, **kwargs) -> Tuple[str, Tuple[str, ...]]:
    sig = inspect.signature(func)
    return func(**{k: v for k, v in kwargs.items() if k in sig.parameters})


def subject(
    id: Optional[str],
    exist_query: Optional[Callable],
    nombre_sujeto: str,
    nombre_id: str,
    *,
    db_name: str = "crit",
) -> Optional[Dict[str, str]]:
    if not id or not exist_query:
        return None

    logger.info(f"Buscando datos para {nombre_sujeto} con {nombre_id}: '{id}'")

    try:
        with connections[db_name].cursor() as cursor:
            sujeto = exist_query(id, cursor) if exist_query else None
    except OperationalError as e:
        logger.error(f"Error al obtener datos para ID: '{id}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Error al obtener datos del ID: '{id}': {str(e)}")
        raise AjaxException()

    if not sujeto:
        message = f"❌ No se encontró ningún {nombre_sujeto} con ese {nombre_id}."
        logger.info(message)
        raise AjaxException(message, causa="ID Inexistente")

    return {
        f"Nombre de {nombre_sujeto.capitalize()}": sujeto.get("nombre", "").title(),
        nombre_id.capitalize(): sujeto.get("id", ""),
    }


def all_objects(
    id: Optional[str],
    fecha: Optional[datetime],
    data_query: Optional[Callable],
    nombre_objetos: str,
    nombre_id: str,
    *,
    db_name: str = "crit",
) -> Optional[List[Dict]]:
    if not data_query:
        return None

    query, params = evaluate_query(data_query, id=id, fecha=fecha)
    logger.debug(f"Ejecutando consulta: '{query}', con parámetros: '{params}'.")

    try:
        with connections[db_name].cursor() as cursor:
            cursor.execute(query, params)
            columnas = tuple(col[0] for col in cursor.description)
            objetos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
    except OperationalError as e:
        logger.error(f"Error al obtener objetos para ID: '{id}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Error al obtener objetos para ID: '{id}': {str(e)}")
        raise AjaxException()

    if not objetos:
        if fecha:
            message = (
                f"❌ No se encontraron {nombre_objetos} con la fecha especificada."
            )
        else:
            message = f"❌ No se encontraron {nombre_objetos} para este {nombre_id}."
        logger.info(message)
        raise AjaxException(
            message, target="fecha" if fecha else "id", causa="Sin resultados"
        )

    logger.info(f"Se encontraron {len(objetos)} objetos para ID: '{id}'")
    return objetos


def formatted_row(dato: str, formatear: Optional[str] = None) -> str:
    if not formatear:
        return dato
    if formatear == "nombre":
        return dato.title()
    if formatear == "fecha":
        return (
            dato.strftime("%d/%m/%Y %H:%M") if isinstance(dato, datetime) else str(dato)
        )
    return dato


def filtered_objects(
    objetos: Optional[List[Dict[str, Any]]],
    campos: List[str],
    sql_campos: Dict[str, Any],
) -> Optional[Tuple[Tuple, ...]]:
    if not objetos:
        return None

    return tuple(
        tuple(
            (
                formatted_row(objeto.get(campo), sql_campos[campo].get("formatear"))
                if campo in sql_campos
                else ""
            )
            for campo in campos
        )
        for objeto in objetos
    )


def filename(
    previous_context: Dict[str, Optional[str]],
    ext: str,
    keys: Tuple[str, ...] = (
        "nombre_objetos",
        "nombre_sujeto",
        "id",
        "fecha",
    ),
    buffer=None,
    sep: str = "_",
):
    parts = tuple(previous_context.get(k) for k in keys)
    content_hash = hashlib.sha1(buffer).hexdigest()[:10] if buffer else None
    return sep.join(filter(None, parts + (content_hash,))).replace(" ", sep) + f".{ext}"


def output_path(dir: str, filename: str) -> str:
    output_dir = os.path.join(settings.MEDIA_ROOT, dir)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)


def whatsapp_payload(number: str, mensaje: str, filename: str) -> Dict:
    return {
        "number": "521" + re.sub(r"\D", "", number) + "@c.us",
        "message": mensaje,
        "image_path": f"media/pdf/{filename}",
    }
