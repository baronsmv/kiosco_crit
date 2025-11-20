import os
import re
from typing import Dict, Optional

from django.core.exceptions import ValidationError

from classes.contexts import IdSubContext
from .logger import get_logger

logger = get_logger(__name__)


def id_patterns(id: str, max_length: int, pattern: str) -> None:
    if len(id) > max_length:
        raise ValidationError("El ID es demasiado largo.")
    if not re.match(pattern, id):
        raise ValidationError("El ID contiene caracteres inválidos.")


def id_by_context(id: str, id_context: Optional[IdSubContext] = None) -> bool:
    if not id_context:
        return True
    try:
        id_patterns(
            id=id,
            max_length=id_context.max_length,
            pattern=id_context.pattern,
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
