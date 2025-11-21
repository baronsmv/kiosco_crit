from django.http import HttpRequest, HttpResponse

from utils.logger import get_logger
from . import forms, contexts, sql, selections
from .utils import query_view

logger = get_logger(__name__)


def citas_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        context_list=contexts.citas_paciente,
        selection_list=selections.citas_paciente,
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
        context_list=contexts.datos_paciente,
        selection_list=selections.datos_paciente,
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
        context_list=contexts.citas_colaborador,
        selection_list=selections.citas_colaborador,
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
        context_list=contexts.espacios_disponibles,
        selection_list=selections.espacios_disponibles,
        form=forms.BuscarFechaForm,
        data_query=sql.data.espacios_disponibles,
        nombre_objetos="espacios disponibles",
    )
