from typing import Optional, Dict

from utils.logger import get_logger
from .utils import subject_exists

logger = get_logger(__name__)


def paciente(carnet: str, cursor) -> Optional[Dict[str, str]]:
    logger.info(f"Buscando paciente con carnet: {carnet}")
    return subject_exists(
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
    return subject_exists(
        query="""
              SELECT NB_USUARIO, NB_PATERNO, NB_MATERNO
              FROM SCRITS2.C_USUARIO
              WHERE CL_LOGIN = %s
              """,
        id=id,
        cursor=cursor,
    )
