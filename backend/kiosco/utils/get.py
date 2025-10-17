import inspect
import re
from datetime import date
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

import requests
from django.conf import settings
from django.db import connections, OperationalError
from django.http import HttpRequest
from django.urls import reverse_lazy

from .logger import get_logger
from ..utils import format, map

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
        "mensaje_error": "",
        "error_target": "",
    }


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


def _eval_query(func: Callable, **kwargs) -> Tuple[str, Tuple[str, ...]]:
    sig = inspect.signature(func)
    return func(**{k: v for k, v in kwargs.items() if k in sig.parameters})


def _get_filas(
    id: Optional[str],
    fecha: Optional[datetime],
    exist_func: Callable,
    query_func: Callable,
    db_name: str = "crit",
) -> Optional[Tuple]:
    logger.info(
        f"Buscando filas para ID: '{id}' con fecha '{fecha}'"
        + f" en base de datos: '{db_name}'"
    )
    query, params = _eval_query(query_func, id=id, fecha=fecha)
    try:
        with connections[db_name].cursor() as cursor:
            sujeto = exist_func(id, cursor) if exist_func else None
            if exist_func and not sujeto:
                logger.warning(f"No se encontró sujeto con ID: '{id}'.")
                return None
            logger.debug(
                f"Ejecutando consulta: '{query}',\ncon parámetros: '{params}'."
            )
            cursor.execute(query, params)
            resultados = cursor.fetchall()
        logger.info(f"Se encontraron {len(resultados)} filas para ID: '{id}'")
        return sujeto, resultados
    except OperationalError as e:
        logger.error(f"Error al obtener filas para ID: '{id}': {e}")
        raise
    except Exception as e:
        logger.exception(f"Error al obtener filas para ID: '{id}': {str(e)}")
        return None


def datos(
    id: Optional[str],
    fecha: Optional[datetime],
    sql_campos: Dict,
    exist_query: Optional[Callable],
    data_query: Callable,
) -> Optional[Dict[str, Any]]:
    logger.info(f"Iniciando obtención de datos para ID: {id}")

    filas = _get_filas(
        id=id, fecha=fecha, exist_func=exist_query, query_func=data_query
    )
    if not filas:
        logger.warning(f"No se encontraron datos para ID: {id}")
        return None

    sujeto, objetos = filas

    if sujeto:
        logger.debug(
            f"Procesando {len(objetos)} objetos para: {sujeto.get('nombre', 'Desconocido')}"
        )
    else:
        logger.debug(f"Procesando {len(objetos)} objetos sin sujeto asociado.")

    objetos_formateados = tuple(
        {
            campo: format.campo(cita[i], sql_campos[campo].get("formatear"))
            for i, campo in enumerate(sql_campos.keys())
        }
        for cita in objetos
    )
    logger.info("Datos procesados correctamente.")

    return {
        "sujeto_sf": sujeto or {},
        "objetos_sf": objetos_formateados,
    }


def whatsapp_payload(number: str, mensaje: str, filename: str) -> Dict:
    return {
        "number": "521" + re.sub(r"\D", "", number) + "@c.us",
        "message": mensaje,
        "image_path": f"media/pdfs/{filename}",
    }
