from datetime import date
from typing import Dict, Tuple, Optional

from classes.selections import SelectionList
from utils.logger import get_logger

logger = get_logger(__name__)


def subject_exists(query: str, id: str, cursor) -> Optional[Dict[str, str]]:
    logger.debug(f"Ejecutando búsqueda con ID: {id}")
    logger.debug(f"Query:\n{query.strip()}")

    cursor.execute(query, (id,))
    row = cursor.fetchone()

    if row:
        nombre = " ".join(row)
        logger.info(f"Registro encontrado: {nombre}")
        return {"nombre": nombre, "id": id}
    else:
        logger.warning(f"No se encontró registro para ID: {id}")
        return None


def sql_selection(selection: SelectionList, sep: str = f",\n{' ' * 12}") -> str:
    return sep.join(
        f"{select.sql_expression} AS {select.sql_name}" for select in selection.sql
    )


def parse_query(
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
