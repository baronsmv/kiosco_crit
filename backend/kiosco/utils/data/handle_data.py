from datetime import datetime
from typing import Dict, Optional, Callable, Tuple, Any, List

from django.db import connections

from ..config import cfg_mapeo_estatus


def formatear_dato(dato, tipo: Optional[str] = None) -> str:
    if tipo == "fecha":
        return (
            dato.strftime("%d/%m/%Y %H:%M") if isinstance(dato, datetime) else str(dato)
        )
    if tipo == "estatus":
        return cfg_mapeo_estatus.get(dato, dato)
    return dato


def obtener_filas(
    id: str,
    exist_func: Callable,
    query_func: Callable,
    fecha: Optional[datetime] = None,
    db_name: str = "crit",
) -> Optional[Tuple]:
    with connections[db_name].cursor() as cursor:
        persona = exist_func(id, cursor)
        if not persona:
            return
        cursor.execute(*query_func(id, fecha=fecha))
        return persona, cursor.fetchall()


def obtener_datos(
    id: str,
    campos: Dict,
    exist_func: Callable,
    query_func: Callable,
    fecha: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    filas = obtener_filas(id, exist_func=exist_func, query_func=query_func, fecha=fecha)
    if not filas:
        return None
    persona, objetos = filas

    return {
        "persona_sf": persona,
        "objetos_sf": [
            {
                campo: formatear_dato(cita[i], campos[campo].get("tipo"))
                for i, campo in enumerate(campos.keys())
            }
            for cita in objetos
        ],
    }


def formatear_datos(
    persona_sf: Dict[str, str],
    objetos_sf: List[Dict[str, Any]],
    campos: List[str],
) -> Dict[str, Dict[str, str] | Tuple[Tuple]]:
    return {
        "persona": {
            "Nombre": persona_sf.get("nombre", ""),
            "Carnet": persona_sf.get("id", ""),
        },
        "tabla": tuple(
            tuple(objeto.get(campo, "") for campo in campos) for objeto in objetos_sf
        ),
    }
