from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Callable

from django.db import connections

from .config import citas_sql

citas_mapeo_campos: Dict[str, Dict[str, str]] = citas_sql["campos"]
citas_mapeo_estatus: Dict[str, str] = citas_sql["mapeo_estatus"]


def formatear_dato(dato, tipo: Optional[str] = None) -> str:
    if tipo == "fecha":
        return (
            dato.strftime("%d/%m/%Y %H:%M") if isinstance(dato, datetime) else str(dato)
        )
    if tipo == "estatus":
        return citas_mapeo_estatus.get(dato, dato)
    return dato


def existe_paciente(carnet: str, cursor) -> Optional[Dict[str, str]]:
    cursor.execute(
        """
        SELECT NB_PACIENTE, NB_PATERNO, NO_CARNET
        FROM SCRITS2.C_PACIENTE
        WHERE NO_CARNET = %s
        """,
        (carnet,),
    )
    row = cursor.fetchone()
    return (
        {
            "nombre": f"{row[0]} {row[1]}",
            "no_carnet": row[2],
        }
        if row
        else None
    )


def query_citas(
    carnet: str,
    fecha: Optional[datetime],
    campos: List[str] = citas_mapeo_campos.keys(),
) -> Tuple[str, Tuple]:
    for campo in campos:
        if campo not in citas_mapeo_campos:
            raise ValueError(f"Campo desconocido: {campo}")

    select_clause = ", ".join(citas_mapeo_campos[c]["sql"] + f" AS {c}" for c in campos)

    query = f"""
        SELECT {select_clause}
        FROM SCRITS2.C_PACIENTE cp
        INNER JOIN SCRITS2.K_PACIENTE_CITA kpc ON cp.FL_PACIENTE = kpc.FL_PACIENTE
        INNER JOIN SCRITS2.K_CITA kc ON kpc.FL_CITA = kc.FL_CITA
        INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
        INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
        INNER JOIN SCRITS2.C_CLINICA cc ON cp.FL_CLINICA = cc.FL_CLINICA
        WHERE cp.NO_CARNET = %s
    """

    params: Tuple = (carnet,)
    if fecha:
        query += (
            " AND kpc.CL_ESTATUS_CITA IN ('A', 'N') AND CAST(kc.FE_CITA AS DATE) = %s"
        )
        params += (fecha,)
    else:
        query += " AND kpc.CL_ESTATUS_CITA = 'A'"

    query += " ORDER BY kc.FE_CITA DESC"
    return query, params


def obtener_filas(
    id: str,
    exist_func: Callable,
    query_func: Callable,
    campos: List[str],
    fecha: Optional[datetime] = None,
    db_name: str = "crit",
) -> Optional[Tuple]:
    with connections[db_name].cursor() as cursor:
        persona = exist_func(id, cursor)
        if not persona:
            return None
        cursor.execute(*query_func(id, campos=campos, fecha=fecha))
        return persona, cursor.fetchall()


def obtener_citas(
    carnet: str,
    campos: List[str] = citas_mapeo_campos.keys(),
    fecha: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    filas = obtener_filas(
        carnet,
        exist_func=existe_paciente,
        query_func=query_citas,
        campos=campos,
        fecha=fecha,
    )
    if not filas:
        return None
    paciente, citas = filas

    return {
        "paciente_sf": paciente,
        "citas_sf": [
            {
                campo: formatear_dato(cita[i], citas_mapeo_campos[campo].get("tipo"))
                for i, campo in enumerate(campos)
            }
            for cita in citas
        ],
    }


def formatear_citas(
    paciente_sf: Dict[str, str],
    citas_sf: List[Dict[str, Any]],
    campos: List[str] = citas_mapeo_campos.keys(),
) -> Dict[str, Dict[str, str] | Tuple[Tuple]]:
    return {
        "persona": {
            "Nombre": paciente_sf.get("nombre", ""),
            "Carnet": paciente_sf.get("no_carnet", ""),
        },
        "tabla": tuple(
            tuple(cita.get(campo, "") for campo in campos) for cita in citas_sf
        ),
    }
