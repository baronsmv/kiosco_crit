from datetime import datetime
from typing import Tuple, Optional, Dict

from ..utils import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


def _select(campos: Dict) -> str:
    seleccion = ", ".join(campos[c]["sql"] + f" AS {c}" for c in campos.keys())
    logger.debug(f"Campos seleccionados para query: {seleccion}")
    return seleccion


def _parse_query(
    query: str,
    id: Optional[str] = None,
    fecha: Optional[datetime] = None,
    filters: Optional[Dict] = None,
    order_by: Optional[str] = None,
) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Generando consulta para ID: {id} con fecha: {fecha}")
    params = tuple(filter(None, (id, fecha)))

    if fecha:
        query += " AND CAST(kc.FE_CITA AS DATE) = %s"
        logger.debug("Agregado filtro adicional por fecha exacta.")

    if filters:
        for k, v in filters.items():
            if fecha:
                valores = v.get("con_fecha")
            else:
                valores = v.get("sin_fecha")
            if valores:
                query += f" AND {k} IN ('" + "', '".join(valores) + "')"

    if order_by:
        query += f" ORDER BY {order_by}"

    logger.debug(f"Query final generado: {query}")
    logger.debug(f"Parámetros: {params}")

    return query, params


def citas_carnet(
    carnet: str,
    fecha: Optional[datetime],
) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de citas por carnet: {carnet}, fecha: {fecha}")
    cfg = config.cfg_citas_paciente.get("sql", {})
    query = f"""
        SELECT {_select(cfg.get("campos", {}))}
        FROM SCRITS2.C_PACIENTE cp
        INNER JOIN SCRITS2.K_PACIENTE_CITA kpc ON cp.FL_PACIENTE = kpc.FL_PACIENTE
        INNER JOIN SCRITS2.K_CITA kc ON kpc.FL_CITA = kc.FL_CITA
        INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
        INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
        INNER JOIN SCRITS2.C_CLINICA cc ON cp.FL_CLINICA = cc.FL_CLINICA
        LEFT JOIN SCRITS2.C_ESTATUS_CITA cec ON kpc.CL_ESTATUS_CITA = cec.CL_ESTATUS_CITA
        WHERE cp.NO_CARNET = %s
    """
    return _parse_query(
        query=query,
        id=carnet,
        fecha=fecha,
        filters=cfg.get("filtros", {}),
        order_by="kc.FE_CITA ASC",
    )


def citas_colaborador(
    id: str, fecha: Optional[datetime]
) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de citas por colaborador ID: {id}, fecha: {fecha}")
    cfg = config.cfg_citas_colaborador.get("sql", {})
    query = f"""
        SELECT {_select(cfg.get("campos", {}))}
        FROM SCRITS2.K_CITA kc
        INNER JOIN SCRITS2.C_USUARIO cu ON kc.FL_USUARIO = cu.FL_USUARIO
        INNER JOIN SCRITS2.C_SERVICIO cs ON kc.FL_SERVICIO = cs.FL_SERVICIO
        LEFT JOIN SCRITS2.K_PACIENTE_CITA kpc ON kc.FL_CITA = kpc.FL_CITA
        LEFT JOIN SCRITS2.C_PACIENTE cp ON kpc.FL_PACIENTE = cp.FL_PACIENTE
        LEFT JOIN SCRITS2.C_CLINICA cc ON cp.FL_CLINICA = cc.FL_CLINICA
        LEFT JOIN SCRITS2.C_ESTATUS_CITA cec ON kpc.CL_ESTATUS_CITA = cec.CL_ESTATUS_CITA
        WHERE cu.CL_LOGIN= %s
    """
    return _parse_query(
        query=query,
        id=id,
        fecha=fecha,
        filters=cfg.get("filtros", {}),
        order_by="kc.FE_CITA ASC",
    )


def espacios_disponibles(fecha: datetime) -> Tuple[str, Tuple[str, ...]]:
    logger.info(f"Construyendo query de espacios disponibles por fecha: {fecha}")
    cfg = config.cfg_espacios.get("sql", {})
    query = f"""
        SELECT {_select(cfg.get("campos", {}))}
        FROM SCRITS2.K_CITA kc
        INNER JOIN SCRITS2.C_SERVICIO cs
        ON kc.FL_SERVICIO = cs.FL_SERVICIO
        INNER JOIN SCRITS2.C_USUARIO cu
        ON kc.FL_USUARIO = cu.FL_USUARIO
        WHERE kc.NO_DISPONIBLES > 0
    """
    return _parse_query(
        query=query,
        fecha=fecha,
        filters=cfg.get("filtros", {}),
        order_by="kc.FE_CITA ASC",
    )
