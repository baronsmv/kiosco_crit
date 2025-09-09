from datetime import datetime
from typing import Tuple, Optional

from ..config import cfg_citas_carnet, cfg_citas_colaborador
from ..logger import get_logger

logger = get_logger(__name__)


def select(campos):
    seleccion = ", ".join(campos[c]["sql"] + f" AS {c}" for c in campos.keys())
    logger.debug(f"Campos seleccionados para query: {seleccion}")
    return seleccion


def citas(query, id, fecha, if_fecha: Tuple[str, str]):
    logger.info(f"Generando consulta para ID: {id} con fecha: {fecha}")

    params: Tuple = (id, fecha) if fecha else (id,)
    filtro = if_fecha[0 if fecha else 1]
    query += filtro
    logger.debug(f"Filtro aplicado según si se proporciona fecha: {filtro}")

    if fecha:
        query += " AND CAST(kc.FE_CITA AS DATE) = %s"
        logger.debug("Agregado filtro adicional por fecha exacta.")

    query += " ORDER BY kc.FE_CITA ASC"

    logger.debug(f"Query final generado: {query}")
    logger.debug(f"Parámetros: {params}")

    return query, params


def citas_carnet(
    carnet: str,
    fecha: Optional[datetime],
) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de citas por carnet: {carnet}, fecha: {fecha}")
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
    logger.info(f"Construyendo query de citas por colaborador ID: {id}, fecha: {fecha}")
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
