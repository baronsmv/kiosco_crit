import os
import re
from typing import Dict, Optional

from django.core.exceptions import ValidationError

from .logger import get_logger

logger = get_logger(__name__)


def id_pattern(id: str, max_length: int, pattern: str) -> None:
    if len(id) > max_length:
        raise ValidationError("El ID es demasiado largo.")
    if not re.match(pattern, id):
        raise ValidationError("El ID contiene caracteres inválidos.")


def id(id: str, context: Optional[Dict] = None) -> bool:
    context = context or {}
    try:
        id_pattern(
            id=id,
            max_length=context.get("id_max_length", 20),
            pattern=context.get("id_pattern", r"^[a-zA-Z0-9. \-]+$"),
        )
        return True
    except ValidationError:
        return False


def context(context: Optional[Dict]) -> None:
    if not context:
        logger.error("El contexto en sesión está vacío. No se puede generar PDF.")
        raise ValueError("No hay datos de contexto en sesión.")

    logger.debug(f"Contexto en sesión recibido: {context.keys()}")


def output_file(path: str) -> None:
    if not os.path.exists(path):
        logger.error(f"El archivo no fue creado: {path}")
        raise FileNotFoundError("No se pudo generar el archivo.")
