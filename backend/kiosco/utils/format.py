from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

from .logger import get_logger

logger = get_logger(__name__)


def campo(dato: str, formatear: Optional[str] = None) -> str:
    if not formatear:
        return dato
    if formatear == "nombre":
        return dato.title()
    if formatear == "fecha":
        return (
            dato.strftime("%d/%m/%Y %H:%M") if isinstance(dato, datetime) else str(dato)
        )
    return dato


def campos(
    persona_sf: Dict[str, str],
    objetos_sf: List[Dict[str, Any]],
    campos: List[str],
    persona: str,
    identificador: str,
) -> Dict[str, Dict[str, str] | Tuple[Tuple]]:
    logger.debug(f"Formateando datos finales. Campos: {campos}")

    resultado = {
        "persona": {
            f"Nombre de {persona.capitalize()}": persona_sf.get("nombre", "").title(),
            identificador.capitalize(): persona_sf.get("id", ""),
        },
        "tabla": tuple(
            tuple(objeto.get(campo, "") for campo in campos) for objeto in objetos_sf
        ),
    }

    logger.info("Formato final completado.")
    return resultado
