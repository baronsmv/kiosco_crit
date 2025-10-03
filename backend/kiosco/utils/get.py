import inspect
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

from django.db import connections, OperationalError
from django.http import HttpRequest

from .logger import get_logger

logger = get_logger(__name__)


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


def _obtener_filas(
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
            persona = exist_func(id, cursor) if exist_func else None
            if exist_func and not persona:
                logger.warning(f"No se encontró persona con ID: '{id}'.")
                return None
            logger.debug(
                f"Ejecutando consulta: '{query}',\ncon parámetros: '{params}'."
            )
            cursor.execute(query, params)
            resultados = cursor.fetchall()
        logger.info(f"Se encontraron {len(resultados)} filas para ID: '{id}'")
        return persona, resultados
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
    exist_func: Optional[Callable],
    query_func: Callable,
) -> Optional[Dict[str, Any]]:
    logger.info(f"Iniciando obtención de datos para ID: {id}")

    filas = _obtener_filas(
        id=id, fecha=fecha, exist_func=exist_func, query_func=query_func
    )
    if not filas:
        logger.warning(f"No se encontraron datos para ID: {id}")
        return None

    persona, objetos = filas

    if persona:
        logger.debug(
            f"Procesando {len(objetos)} objetos para: {persona.get('nombre', 'Desconocido')}"
        )
    else:
        logger.debug(f"Procesando {len(objetos)} objetos sin persona asociada")

    objetos_formateados = tuple(
        {
            campo: campo(cita[i], sql_campos[campo].get("formatear"))
            for i, campo in enumerate(sql_campos.keys())
        }
        for cita in objetos
    )
    logger.info("Datos procesados correctamente.")

    return {
        "persona_sf": persona or {},
        "objetos_sf": objetos_formateados,
    }
