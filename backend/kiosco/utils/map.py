from typing import Dict, Tuple

from .logger import get_logger

logger = get_logger(__name__)


def columns(data: Dict[str, Dict], mapeo: Dict[str, Dict]) -> Tuple:
    campos = data.get("campos", {})
    mapeo_campos = mapeo["campos"]

    logger.debug(f"Mapeando columnas: {list(campos)}")

    for campo in campos:
        if campo not in mapeo_campos:
            logger.error(f"Campo desconocido en mapeo: {campo}")
            raise ValueError(f"Campo desconocido: {campo}")

    columnas = tuple(mapeo_campos[campo]["nombre"] for campo in campos)
    logger.debug(f"Columnas mapeadas: {columnas}")
    return columnas
