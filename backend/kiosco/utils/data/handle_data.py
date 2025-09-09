from datetime import datetime
from typing import Dict, Optional, Callable, Tuple, Any, List

from django.db import connections

from ..logger import get_logger

logger = get_logger(__name__)


def obtener_filas(
    id: str,
    exist_func: Callable,
    query_func: Callable,
    fecha: Optional[datetime] = None,
    db_name: str = "crit",
) -> Optional[Tuple]:
    logger.info(f"Buscando filas para ID: {id} en base de datos: {db_name}")
    try:
        with connections[db_name].cursor() as cursor:
            persona = exist_func(id, cursor)
            if not persona:
                logger.warning(f"No se encontró persona con ID: '{id}'.")
                return None

            query, params = query_func(id, fecha=fecha)
            logger.debug(
                f"Ejecutando consulta: '{query}',\ncon parámetros: '{params}'."
            )
            cursor.execute(query, params)

            resultados = cursor.fetchall()
            logger.info(f"Se encontraron {len(resultados)} filas para ID: '{id}'")
            return persona, resultados
    except Exception as e:
        logger.exception(f"Error al obtener filas para ID: '{id}': {str(e)}")
        return None


def obtener_datos(
    id: str,
    sql_campos: Dict,
    exist_func: Callable,
    query_func: Callable,
    fecha: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    logger.info(f"Iniciando obtención de datos para ID: {id}")

    filas = obtener_filas(id, exist_func=exist_func, query_func=query_func, fecha=fecha)
    if not filas:
        logger.warning(f"No se encontraron datos para ID: {id}")
        return None

    persona, objetos = filas
    logger.debug(
        f"Procesando {len(objetos)} objetos para: {persona.get('nombre', 'Desconocido')}"
    )

    objetos_formateados = [
        {campo: cita[i] for i, campo in enumerate(sql_campos.keys())}
        for cita in objetos
    ]
    logger.info(f"Datos procesados correctamente para ID: {id}")

    return {
        "persona_sf": persona,
        "objetos_sf": objetos_formateados,
    }


def formatear_datos(
    persona_sf: Dict[str, str],
    objetos_sf: List[Dict[str, Any]],
    campos: List[str],
) -> Dict[str, Dict[str, str] | Tuple[Tuple]]:
    logger.debug(f"Formateando datos finales. Campos: {campos}")

    resultado = {
        "persona": {
            "Nombre": persona_sf.get("nombre", ""),
            "Carnet": persona_sf.get("id", ""),
        },
        "tabla": tuple(
            tuple(objeto.get(campo, "") for campo in campos) for objeto in objetos_sf
        ),
    }

    logger.info("Formato final completado.")
    return resultado
