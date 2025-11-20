from datetime import date
from typing import Optional

from django.http import HttpRequest, JsonResponse

from utils import config
from .utils import api_query_view
from .. import sql


def api_citas_paciente(
    request: HttpRequest, id: str, fecha: Optional[date] = None
) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_citas_paciente,
        exist_query=sql.exist.paciente,
        data_query=sql.data.citas_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="citas",
        url_params={"id": id, "fecha": fecha},
    )


def api_datos_paciente(request: HttpRequest, id: str) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_datos_paciente,
        exist_query=sql.exist.paciente,
        data_query=sql.data.datos_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="datos",
        url_params={"id": id},
    )


def api_citas_colaborador(
    request: HttpRequest, id: str, fecha: Optional[date] = None
) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_citas_colaborador,
        exist_query=sql.exist.colaborador,
        data_query=sql.data.citas_colaborador,
        nombre_id="nombre de usuario",
        nombre_sujeto="colaborador",
        nombre_objetos="citas",
        url_params={"id": id, "fecha": fecha},
    )


def api_espacios_disponibles(
    request: HttpRequest, fecha: date = date.today()
) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_espacios_disponibles,
        data_query=sql.data.espacios_disponibles,
        nombre_objetos="espacios disponibles",
        url_params={"fecha": fecha},
    )
