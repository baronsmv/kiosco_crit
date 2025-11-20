from django.http import HttpRequest, HttpResponse

from utils import config
from utils.logger import get_logger
from . import forms, sql
from .utils import query_view

logger = get_logger(__name__)


def citas_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        config_data=config.cfg_citas_paciente,
        form=forms.BuscarIdFechaForm,
        exist_query=sql.exist.paciente,
        data_query=sql.data.citas_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="citas",
    )


def datos_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        config_data=config.cfg_datos_paciente,
        form=forms.BuscarIdForm,
        exist_query=sql.exist.paciente,
        data_query=sql.data.datos_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="datos",
    )


def citas_colaborador(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        config_data=config.cfg_citas_colaborador,
        form=forms.BuscarIdFechaForm,
        exist_query=sql.exist.colaborador,
        data_query=sql.data.citas_colaborador,
        nombre_id="nombre de usuario",
        nombre_sujeto="colaborador",
        nombre_objetos="citas",
    )


def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        config_data=config.cfg_espacios_disponibles,
        form=forms.BuscarFechaForm,
        data_query=sql.data.espacios_disponibles,
        nombre_objetos="espacios disponibles",
    )
