from datetime import datetime
from typing import Optional

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
