from typing import Optional, Dict

from ..utils.logger import get_logger

logger = get_logger(__name__)


def _exists(query: str, id: str, cursor) -> Optional[Dict[str, str]]:
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


def paciente(carnet: str, cursor) -> Optional[Dict[str, str]]:
    logger.info(f"Buscando paciente con carnet: {carnet}")
    return _exists(
        query="""
              SELECT NB_PACIENTE, NB_PATERNO, NB_MATERNO
              FROM SCRITS2.C_PACIENTE
              WHERE NO_CARNET = %s
              """,
        id=carnet,
        cursor=cursor,
    )


def colaborador(id: str, cursor) -> Optional[Dict[str, str]]:
    logger.info(f"Buscando colaborador con login: {id}")
    return _exists(
        query="""
              SELECT NB_USUARIO, NB_PATERNO, NB_MATERNO
              FROM SCRITS2.C_USUARIO
              WHERE CL_LOGIN = %s
              """,
        id=id,
        cursor=cursor,
    )
