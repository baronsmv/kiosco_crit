from typing import Dict, Optional

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
