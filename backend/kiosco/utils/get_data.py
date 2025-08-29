from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from django.db import connections

from .config import citas_sql

mapeo_campos: Dict[str, Dict[str, str]] = citas_sql["campos"]
mapeo_estatus: Dict[str, str] = citas_sql["mapeo_estatus"]


def formatear_dato(dato, tipo: Optional[str] = None) -> str:
    if tipo == "fecha":
        return (
            dato.strftime("%d/%m/%Y %H:%M") if isinstance(dato, datetime) else str(dato)
        )
    if tipo == "estatus":
        return mapeo_estatus.get(dato, dato)
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
    carnet: str, fecha: Optional[datetime], campos: List[str] = mapeo_campos.keys()
) -> Tuple[str, Tuple]:
    for campo in campos:
        if campo not in mapeo_campos:
            raise ValueError(f"Campo desconocido: {campo}")

    select_clause = ", ".join(mapeo_campos[c]["sql"] + f" AS {c}" for c in campos)

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


def obtener_citas(
    carnet: str,
    campos: List[str] = mapeo_campos.keys(),
    fecha: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    with connections["crit"].cursor() as cursor:
        paciente = existe_paciente(carnet, cursor)
        if not paciente:
            return None

        query, params = query_citas(carnet, campos=campos, fecha=fecha)
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return {
        "paciente_sf": paciente,
        "citas_sf": [
            {
                campo: formatear_dato(row[i], mapeo_campos[campo].get("tipo"))
                for i, campo in enumerate(campos)
            }
            for row in rows
        ],
    }


def formatear_citas(
    paciente_sf: Dict[str, str],
    citas_sf: List[Dict[str, Any]],
    campos: List[str] = mapeo_campos.keys(),
) -> Dict[str, Dict[str, str] | Tuple[Tuple]]:
    return {
        "paciente": {
            "Nombre": paciente_sf.get("nombre", ""),
            "Carnet": paciente_sf.get("no_carnet", ""),
        },
        "tabla": tuple(
            tuple(cita.get(campo, "") for campo in campos) for cita in citas_sf
        ),
    }
