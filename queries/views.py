from django.http import HttpRequest, HttpResponse

from utils.logger import get_logger
from . import forms, contexts, selections
from .sql import queries
from .utils import query_view

logger = get_logger(__name__)


def citas_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        context_list=contexts.citas_paciente,
        selection_list=selections.citas_paciente,
        form=forms.BuscarIdFechaForm,
        data_query=queries.citas_paciente,
    )


def datos_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        context_list=contexts.datos_paciente,
        selection_list=selections.datos_paciente,
        form=forms.BuscarIdForm,
        data_query=queries.datos_paciente,
    )


def citas_colaborador(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        context_list=contexts.citas_colaborador,
        selection_list=selections.citas_colaborador,
        form=forms.BuscarIdFechaForm,
        data_query=queries.citas_colaborador,
    )


def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        context_list=contexts.espacios_disponibles,
        selection_list=selections.espacios_disponibles,
        form=forms.BuscarFechaForm,
        data_query=queries.espacios_disponibles,
    )
