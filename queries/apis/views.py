from django.http import HttpRequest, JsonResponse

from utils import config
from .utils import api_query_view
from .. import forms, queries


def api_citas_paciente(request: HttpRequest) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_citas_paciente,
        form=forms.BuscarIdFechaForm,
        exist_query=queries.exist.paciente,
        data_query=queries.data.citas_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="citas",
    )


def api_datos_paciente(request: HttpRequest) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_datos_paciente,
        form=forms.BuscarIdForm,
        exist_query=queries.exist.paciente,
        data_query=queries.data.datos_paciente,
        nombre_id="carnet",
        nombre_sujeto="paciente",
        nombre_objetos="datos",
    )


def api_citas_colaborador(request: HttpRequest) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_citas_colaborador,
        form=forms.BuscarIdFechaForm,
        exist_query=queries.exist.colaborador,
        data_query=queries.data.citas_colaborador,
        nombre_id="nombre de usuario",
        nombre_sujeto="colaborador",
        nombre_objetos="citas",
    )


def api_espacios_disponibles(request: HttpRequest) -> JsonResponse:
    return api_query_view(
        request=request,
        config_data=config.cfg_espacios_disponibles,
        form=forms.BuscarFechaForm,
        data_query=queries.data.espacios_disponibles,
        nombre_objetos="espacios disponibles",
    )
