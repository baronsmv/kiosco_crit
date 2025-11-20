import hashlib
import os
from datetime import datetime
from typing import Dict, Optional, Tuple, List, Any, Union

from django.conf import settings
from django.http import HttpRequest

from . import map
from .logger import get_logger

logger = get_logger(__name__)
base_url = settings.WHATSAPP_API_BASE_URL


def model_type(nombre_objetos: str, nombre_sujeto: str) -> str:
    tipo = nombre_objetos.title()
    if nombre_sujeto:
        tipo += f" de {nombre_sujeto.title()}"
    return tipo


def format_row(dato: Union[str, datetime], formatear: Optional[str] = None) -> str:
    if not formatear:
        return dato
    if formatear == "nombre":
        return dato.title()
    if formatear == "fecha":
        return (
            dato.strftime("%d/%m/%Y %H:%M") if isinstance(dato, datetime) else str(dato)
        )
    return dato


def tabla(
    objetos: Optional[List[Dict[str, Any]]],
    campos: List[str],
    sql_campos: Dict[str, Any],
) -> Optional[Tuple[Tuple, ...]]:
    if not objetos:
        return None

    return tuple(
        tuple(
            (
                format_row(objeto.get(campo), sql_campos[campo].get("formatear"))
                if campo in sql_campos
                else ""
            )
            for campo in campos
        )
        for objeto in objetos
    )


def tabla_with_columns(
    context: Dict,
    data,
    sql_data,
    objetos: Optional[List[Dict[str, Any]]] = None,
) -> None:
    objetos = objetos or context.get("objetos") or None

    context["tabla"] = tabla(
        objetos,
        campos=data.get("campos", {}),
        sql_campos=sql_data.get("campos", {}),
    )
    context["tabla_columnas"] = map.columns(data, sql_data=sql_data)


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
