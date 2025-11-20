import hashlib
import os
from typing import Dict, Optional, Tuple, List, Any

from django.conf import settings
from django.http import HttpRequest

from classes.selections import Selection
from .logger import get_logger

logger = get_logger(__name__)
base_url = settings.WHATSAPP_API_BASE_URL


def model_type(nombre_objetos: str, nombre_sujeto: str) -> str:
    tipo = nombre_objetos.title()
    if nombre_sujeto:
        tipo += f" de {nombre_sujeto.title()}"
    return tipo


def formatted_campo(campo: str, format_option: Optional[str]):
    if not format_option:
        return campo

    if format_option == "name":
        return campo.title()

    return campo


def tabla(
    objetos: Optional[List[Dict[str, Any]]],
    selection: Selection,
    sql_selection: Selection,
) -> Optional[Tuple[Tuple, ...]]:
    if not objetos:
        return None

    return tuple(
        tuple(
            formatted_campo(objeto.get(campo.sql_name), campo.format)
            for campo in selection
            if campo in sql_selection
        )
        for objeto in objetos
    )


def client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR")
    return ip


def filename(
    previous_context: Dict[str, Optional[str]],
    ext: str,
    keys: Tuple[str, ...] = (
        "nombre_objetos",
        "nombre_sujeto",
        "id",
        "fecha",
    ),
    buffer=None,
    sep: str = "_",
) -> str:
    parts = tuple(previous_context.get(k) for k in keys)
    content_hash = hashlib.sha1(buffer).hexdigest()[:10] if buffer else None
    return sep.join(filter(None, parts + (content_hash,))).replace(" ", sep) + f".{ext}"


def output_path(dir: str, filename: str) -> str:
    output_dir = os.path.join(settings.MEDIA_ROOT, dir)
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, filename)
