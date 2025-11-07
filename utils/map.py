from typing import Dict, Tuple

from utils.logger import get_logger

logger = get_logger(__name__)


def columns(render_data: Dict[str, Dict], sql_data: Dict[str, Dict]) -> Tuple[str, ...]:
    campos = render_data.get("campos", {})
    mapeo_campos = sql_data["campos"]

    logger.debug(f"Mapeando columnas: {list(campos)}")

    for campo in campos:
        if campo not in mapeo_campos:
            logger.error(f"Campo desconocido en mapeo: {campo}")
            raise ValueError(f"Campo desconocido: {campo}")

    columnas = tuple(mapeo_campos[campo]["nombre"] for campo in campos)
    logger.debug(f"Columnas mapeadas: {columnas}")
    return columnas
