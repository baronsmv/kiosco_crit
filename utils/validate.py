import os
import re
from datetime import datetime
from typing import Dict, Optional, Type

from django.core.exceptions import ValidationError
from django.forms.forms import Form

from classes.models import BaseModel
from utils.logger import get_logger

logger = get_logger(__name__)


def id_pattern(id: str, max_length: int, pattern: str) -> None:
    if len(id) > max_length:
        raise ValidationError("El ID es demasiado largo.")
    if not re.match(pattern, id):
        raise ValidationError("El ID contiene caracteres inválidos.")


def id(
    id: str,
    fecha: datetime,
    has_fecha: bool,
    context: Dict,
    model: Optional[Type[BaseModel]],
    reg_form: Form,
    ip_cliente: str,
    tipo: str,
) -> bool:
    try:
        id_pattern(
            id=id,
            max_length=context.get("id_max_length", 20),
            pattern=context.get("id_pattern", r"^[a-zA-Z0-9. \-]+$"),
        )
        return True
    except ValidationError as e:
        reg_form.add_error("id", e)
        context.update(
            {
                "id_error": True,
                "date_error": has_fecha and bool(reg_form["fecha"].errors),
            }
        )
        logger.warning(f"Error de validación en ID: {e}")
        if model:
            model.objects.create(
                tipo=tipo,
                identificador=id,
                fecha_especificada=fecha,
                ip_cliente=ip_cliente,
                estado="ID no válido",
            )
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
