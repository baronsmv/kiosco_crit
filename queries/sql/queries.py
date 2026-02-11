from datetime import date
from typing import Tuple, Optional

from classes import joins, tables
from utils.logger import get_logger
from . import selections
from .utils import sql_selection

logger = get_logger(__name__)


def citas_paciente(id: str, fecha: Optional[date]) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de citas por carnet: {id}, fecha: {fecha}")

    id_filter = "WHERE cp.NO_CARNET = %s" if id else ""
    fecha_filter = "AND CAST(kc.FE_CITA AS DATE) = %s" if fecha else ""
    estatus_filter = (
        "AND kpc.CL_ESTATUS_CITA IN ('A','N')"
        if fecha
        else "AND kpc.CL_ESTATUS_CITA IN ('A')"
    )
    order_by = "ORDER BY kc.FE_CITA ASC"

    query = f"""
        SELECT
            {sql_selection(selections.citas_paciente)}
        FROM {tables.cp}
        {joins.cp_kpc.with_extra(estatus_filter)}
        {joins.kpc_kc.with_extra(fecha_filter)}
        {joins.kc_cs}
        {joins.kc_cu}
        {joins.cp_cc}
        {joins.kpc_cec}
        {id_filter}
        {order_by}
    """
    params = tuple(filter(None, (fecha, id)))
    return query, params


def citas_colaborador(id: Optional[str], fecha: Optional[date]) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de citas por colaborador ID: {id}, fecha: {fecha}")

    id_filter = "WHERE cu.CL_LOGIN = %s" if id else ""
    fecha_filter = "AND CAST(kc.FE_CITA AS DATE) = %s" if fecha else ""
    status_filter = "AND kpc.CL_ESTATUS_CITA NOT IN ('C')"
    order_by = "ORDER BY kc.FE_CITA ASC"

    query = f"""
        SELECT
            {sql_selection(selections.citas_colaborador)}
        FROM {tables.cu}
        {joins.cu_kc.with_extra(fecha_filter)}
        {joins.kc_kpc.with_extra(status_filter)}
        {joins.kc_cs}
        {joins.kpc_cp}
        {joins.cp_cc}
        {joins.kpc_cec}
        {id_filter}
        {order_by}
    """
    params = tuple(filter(None, (fecha, id)))
    return query, params


def espacios_disponibles(fecha: date) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de espacios disponibles por fecha: {fecha}")

    fecha_filter = "AND CAST(kc.FE_CITA AS DATE) = %s"
    order_by = "ORDER BY kc.FE_CITA ASC"

    query = f"""
        SELECT
            {sql_selection(selections.espacios_disponibles)}
        FROM {tables.cu}
        {joins.cu_kc.with_extra(fecha_filter)}
        {joins.kc_cs.inner()}
        WHERE
            kc.NO_DISPONIBLES > 0
            AND kc.NO_DURACION >= 30
            AND cs.NB_SERVICIO NOT LIKE '%%dummy%%'
            AND cs.NB_SERVICIO NOT LIKE '%%análisis%%'
            AND cs.NB_SERVICIO NOT LIKE '%%EEG%%'
            AND kc.FG_BLOQUEADA = 0
        {order_by}
    """
    params = tuple(filter(None, (fecha,)))
    return query, params


def datos_paciente(id: Optional[str]) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de datos del paciente por carnet: {id}")

    id_filter = "cp.NO_CARNET = %s AND " if id else ""

    query = f"""
        SELECT
            {sql_selection(selections.datos_paciente)}
        FROM {tables.cp}
        {joins.cp_kpc.inner()}
        {joins.kpc_ksd.inner()}
        {joins.kpc_kc.inner()}
        {joins.cp_cc.inner()}
        {joins.kc_cs.inner()}
        WHERE
            {id_filter}
            ksd.FG_CANCELADO = 0
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
    params = tuple(filter(None, (id,)))
    return query, params


def prescripciones(id: str) -> Tuple[str, Tuple]:
    logger.info(f"Construyendo query de prescripciones por carnet: {id}")

    id_filter = "WHERE cp.NO_CARNET = %s" if id else ""

    query = f"""
    """
    params = tuple(filter(None, (id,)))
    return query, params
