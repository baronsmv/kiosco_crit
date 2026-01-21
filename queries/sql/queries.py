from datetime import date
from typing import Tuple, Optional

from utils.logger import get_logger
from . import selections
from .utils import sql_selection

logger = get_logger(__name__)


def citas_paciente(id: str, fecha: Optional[date]) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de citas por carnet: {id}, fecha: {fecha}")
    fecha_filter = "AND CAST(kc.FE_CITA AS DATE) = %s" if fecha else ""
    estatus_filter = (
        "AND kpc.CL_ESTATUS_CITA IN ('A','N')"
        if fecha
        else "AND kpc.CL_ESTATUS_CITA IN ('A')"
    )

    query = f"""
        SELECT
            {sql_selection(selections.citas_paciente)}
        FROM SCRITS2.C_PACIENTE AS cp
        LEFT JOIN SCRITS2.K_PACIENTE_CITA AS kpc
            ON cp.FL_PACIENTE = kpc.FL_PACIENTE
            {estatus_filter}
        LEFT JOIN SCRITS2.K_CITA AS kc
            ON kpc.FL_CITA = kc.FL_CITA
            {fecha_filter}
        LEFT JOIN SCRITS2.C_SERVICIO AS cs
            ON kc.FL_SERVICIO = cs.FL_SERVICIO
        LEFT JOIN SCRITS2.C_USUARIO AS cu
            ON kc.FL_USUARIO = cu.FL_USUARIO
        LEFT JOIN SCRITS2.C_CLINICA AS cc
            ON cp.FL_CLINICA = cc.FL_CLINICA
        LEFT JOIN SCRITS2.C_ESTATUS_CITA AS cec
            ON kpc.CL_ESTATUS_CITA = cec.CL_ESTATUS_CITA
        WHERE cp.NO_CARNET = %s
        ORDER BY kc.FE_CITA ASC;
    """
    params = (fecha, id) if fecha else (id,)
    return query, params


def citas_colaborador(id: str, fecha: Optional[date]) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de citas por colaborador ID: {id}, fecha: {fecha}")
    fecha_filter = "AND CAST(kc.FE_CITA AS DATE) = %s" if fecha else ""

    query = f"""
        SELECT
            {sql_selection(selections.citas_colaborador)}
        FROM SCRITS2.C_USUARIO AS cu
        LEFT JOIN SCRITS2.K_CITA AS kc
            ON cu.FL_USUARIO = kc.FL_USUARIO {fecha_filter}
        LEFT JOIN SCRITS2.C_SERVICIO AS cs
            ON kc.FL_SERVICIO = cs.FL_SERVICIO
        LEFT JOIN SCRITS2.K_PACIENTE_CITA AS kpc
            ON kc.FL_CITA = kpc.FL_CITA
            AND kpc.CL_ESTATUS_CITA NOT IN ('C')
        LEFT JOIN SCRITS2.C_PACIENTE AS cp
            ON kpc.FL_PACIENTE = cp.FL_PACIENTE
        LEFT JOIN SCRITS2.C_CLINICA AS cc
            ON cp.FL_CLINICA = cc.FL_CLINICA
        LEFT JOIN SCRITS2.C_ESTATUS_CITA AS cec
            ON kpc.CL_ESTATUS_CITA = cec.CL_ESTATUS_CITA
        WHERE cu.CL_LOGIN = %s
        ORDER BY kc.FE_CITA ASC
    """
    params = (fecha, id) if fecha else (id,)
    return query, params


def espacios_disponibles(fecha: date) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de espacios disponibles por fecha: {fecha}")
    query = f"""
        SELECT
            {sql_selection(selections.espacios_disponibles)}
        FROM SCRITS2.C_USUARIO AS cu
        LEFT JOIN SCRITS2.K_CITA AS kc
            ON kc.FL_USUARIO = cu.FL_USUARIO
            AND CAST(kc.FE_CITA AS DATE) = %s
        INNER JOIN SCRITS2.C_SERVICIO AS cs
            ON kc.FL_SERVICIO = cs.FL_SERVICIO
        WHERE 
            kc.NO_DISPONIBLES > 0
            AND kc.NO_DURACION >= 30
            AND cs.NB_SERVICIO NOT LIKE '%%dummy%%'
            AND cs.NB_SERVICIO NOT LIKE '%%análisis%%'
            AND cs.NB_SERVICIO NOT LIKE '%%EEG%%'
            AND kc.FG_BLOQUEADA = 0
        ORDER BY kc.FE_CITA ASC
    """
    params = (fecha,)
    return query, params


def datos_paciente(id: str) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de datos del paciente por carnet: {id}")
    query = f"""
        SELECT
            {sql_selection(selections.datos_paciente)}
        FROM SCRITS2.C_PACIENTE AS cp
        INNER JOIN SCRITS2.K_PACIENTE_CITA AS kpc
            ON cp.FL_PACIENTE = kpc.FL_PACIENTE
        INNER JOIN SCRITS2.K_SERVICIO_DETALLE AS ksd
            ON ksd.FL_PACIENTE_CITA = kpc.FL_PACIENTE_CITA
        INNER JOIN SCRITS2.K_CITA AS kc
            ON kpc.FL_CITA = kc.FL_CITA
        INNER JOIN SCRITS2.C_CLINICA AS cc
            ON cp.FL_CLINICA = cc.FL_CLINICA
        INNER JOIN SCRITS2.C_SERVICIO AS cs
            ON kc.FL_SERVICIO = cs.FL_SERVICIO
        WHERE
            cp.NO_CARNET = %s
            AND ksd.FG_CANCELADO = 0
            AND ksd.MN_TOTAL > ksd.MN_PAGADO
            AND kpc.FG_EXTERNO = 0
            AND (cp.FG_EXTERNO IS NULL OR cp.FG_EXTERNO = 0)
        GROUP BY
            cp.NO_CARNET,
            cp.NB_PACIENTE,
            cp.NB_PATERNO,
            cp.NB_MATERNO,
            cc.DS_CLINICA,
            cp.NO_INASISTENCIAS,
            cp.FE_ULTANIVERSARIO
        HAVING
            SUM(ksd.MN_TOTAL - ksd.MN_PAGADO) > 0
    """
    params = (id,)
    return query, params
