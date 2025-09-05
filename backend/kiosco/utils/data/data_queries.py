from datetime import datetime
from typing import Tuple, Optional

from ..config import cfg_citas_carnet, cfg_citas_colaborador


def select(campos):
    return ", ".join(campos[c]["sql"] + f" AS {c}" for c in campos.keys())


def citas(query, id, fecha, if_fecha: Tuple[str, str]):
    params: Tuple = (id,)
    query += if_fecha[0 if fecha else 1]
    if fecha:
        query += " AND CAST(kc.FE_CITA AS DATE) = %s"
        params += (fecha,)

    query += " ORDER BY kc.FE_CITA ASC"
    return query, params


def citas_carnet(
    carnet: str,
    fecha: Optional[datetime],
) -> Tuple[str, Tuple]:
    query = f"""
        SELECT {select(cfg_citas_carnet["sql"]["campos"])}
        FROM SCRITS2.C_PACIENTE cp
        INNER JOIN SCRITS2.K_PACIENTE_CITA kpc ON cp.FL_PACIENTE = kpc.FL_PACIENTE
        INNER JOIN SCRITS2.K_CITA kc ON kpc.FL_CITA = kc.FL_CITA
        INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
        INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
        INNER JOIN SCRITS2.C_CLINICA cc ON cp.FL_CLINICA = cc.FL_CLINICA
        WHERE cp.NO_CARNET = %s
    """
    return citas(
        query,
        carnet,
        fecha,
        if_fecha=(
            " AND kpc.CL_ESTATUS_CITA IN ('A', 'N')",
            " AND kpc.CL_ESTATUS_CITA = 'A'",
        ),
    )


def citas_colaborador(id: str, fecha: Optional[datetime]) -> Tuple[str, Tuple]:
    query = f"""
        SELECT {select(cfg_citas_colaborador["sql"]["campos"])}
        FROM SCRITS2.K_CITA kc
        INNER JOIN SCRITS2.C_USUARIO cu
        ON kc.FL_USUARIO = cu.FL_USUARIO
        INNER JOIN SCRITS2.C_SERVICIO cs
        ON kc.FL_SERVICIO = cs.FL_SERVICIO
        LEFT JOIN SCRITS2.K_PACIENTE_CITA kpc
        ON kc.FL_CITA = kpc.FL_CITA
        LEFT JOIN SCRITS2.C_PACIENTE cp
        ON kpc.FL_PACIENTE = cp.FL_PACIENTE
        LEFT JOIN SCRITS2.C_CLINICA cc
        ON cp.FL_CLINICA = cc.FL_CLINICA
        LEFT JOIN SCRITS2.C_ESTATUS_CITA cec
        ON kpc.CL_ESTATUS_CITA = cec.CL_ESTATUS_CITA
        WHERE cu.CL_LOGIN= %s
    """
    return citas(query, id, fecha, if_fecha=("", ""))
