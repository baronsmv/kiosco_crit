from datetime import date
from typing import Tuple, Optional

from utils import config
from utils.logger import get_logger
from .utils import parse_query, sql_selection

logger = get_logger(__name__)


def citas_paciente(id: str, fecha: Optional[date]) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de citas por carnet: {id}, fecha: {fecha}")
    sql_config = config.cfg_citas_paciente.get("sql", {})
    query = f"""
        SELECT {sql_selection(sql_config)}
        FROM SCRITS2.C_PACIENTE cp
        INNER JOIN SCRITS2.K_PACIENTE_CITA kpc ON cp.FL_PACIENTE = kpc.FL_PACIENTE
        INNER JOIN SCRITS2.K_CITA kc ON kpc.FL_CITA = kc.FL_CITA
        INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
        INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
        INNER JOIN SCRITS2.C_CLINICA cc ON cp.FL_CLINICA = cc.FL_CLINICA
        LEFT JOIN SCRITS2.C_ESTATUS_CITA cec ON kpc.CL_ESTATUS_CITA = cec.CL_ESTATUS_CITA
        WHERE cp.NO_CARNET = %s
    """
    return parse_query(
        query=query,
        id=id,
        fecha=fecha,
        filters=sql_config.get("filtros", {}),
        order_by="kc.FE_CITA ASC",
    )


def citas_colaborador(id: str, fecha: Optional[date]) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de citas por colaborador ID: {id}, fecha: {fecha}")
    sql_config = config.cfg_citas_colaborador.get("sql", {})
    query = f"""
        SELECT {sql_selection(sql_config)}
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
    return parse_query(
        query=query,
        id=id,
        fecha=fecha,
        filters=sql_config.get("filtros", {}),
        order_by="kc.FE_CITA ASC",
    )


def espacios_disponibles(fecha: date) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de espacios disponibles por fecha: {fecha}")
    sql_config = config.cfg_espacios_disponibles.get("sql", {})
    query = f"""
        SELECT {sql_selection(sql_config)}
        FROM SCRITS2.K_CITA kc
        INNER JOIN SCRITS2.C_SERVICIO cs
            ON kc.FL_SERVICIO = cs.FL_SERVICIO
        INNER JOIN SCRITS2.C_USUARIO cu
            ON kc.FL_USUARIO = cu.FL_USUARIO
        WHERE kc.NO_DISPONIBLES > 0
        AND cs.NB_SERVICIO NOT LIKE '%%dummy%%'
        AND cs.NB_SERVICIO NOT LIKE '%%análisis%%'
        AND cs.NB_SERVICIO NOT LIKE '%%EEG%%'
        AND kc.FG_BLOQUEADA = 0
    """
    return parse_query(
        query=query,
        fecha=fecha,
        filters=sql_config.get("filtros", {}),
        order_by="kc.FE_CITA ASC",
    )


def datos_paciente(id: str) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de datos del paciente por carnet: {id}")
    sql_config = config.cfg_datos_paciente.get("sql", {})
    query = f"""
    SELECT {sql_selection(sql_config)}
    FROM SCRITS2.K_SERVICIO_DETALLE AS ksd
    INNER JOIN SCRITS2.K_PACIENTE_CITA AS kpc 
        ON ksd.FL_PACIENTE_CITA = kpc.FL_PACIENTE_CITA
    INNER JOIN SCRITS2.C_PACIENTE AS cp
        ON kpc.FL_PACIENTE = cp.FL_PACIENTE
    INNER JOIN SCRITS2.K_CITA AS kc
        ON kpc.FL_CITA = kc.FL_CITA
    INNER JOIN SCRITS2.C_CLINICA AS cc
        ON cp.FL_CLINICA = cc.FL_CLINICA
    INNER JOIN SCRITS2.C_SERVICIO AS cs
        ON kc.FL_SERVICIO = cs.FL_SERVICIO
    WHERE cp.NO_CARNET = %s
        AND ksd.FG_CANCELADO = 0
        AND ksd.MN_TOTAL > KSD.MN_PAGADO
        AND (
            cp.CL_ESTATUS = 'A' 
            OR (
                cp.CL_ESTATUS = 'E' 
                AND cp.CL_FORMA_SEGUIMIENTO IS NOT NULL 
                AND cp.FL_TIPO_SEGUIMIENTO IS NOT NULL
            )
        )
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
    return parse_query(
        query=query,
        id=id,
        filters=sql_config.get("filtros", {}),
        order_by="deuda_total_paciente DESC",
    )
