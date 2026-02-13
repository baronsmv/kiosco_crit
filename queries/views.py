from django.http import HttpRequest, HttpResponse

from utils.logger import get_logger
from . import forms, contexts
from .sql import queries, selections
from .utils import query_view

logger = get_logger(__name__)


def citas_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        query=queries.citas_paciente,
        selection_list=selections.citas_paciente,
        context_list=contexts.citas_paciente,
        form=forms.BuscarIdFechaForm,
    )


def prescripciones_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        query=queries.prescripciones,
        selection_list=selections.prescripciones,
        context_list=contexts.prescripciones,
        form=forms.BuscarIdForm,
    )


def datos_paciente(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        query=queries.datos_paciente,
        selection_list=selections.datos_paciente,
        context_list=contexts.datos_paciente,
        form=forms.BuscarIdForm,
    )


def citas_colaborador(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        query=queries.citas_colaborador,
        selection_list=selections.citas_colaborador,
        context_list=contexts.citas_colaborador,
        form=forms.BuscarIdFechaForm,
    )


def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return query_view(
        request=request,
        query=queries.espacios_disponibles,
        selection_list=selections.espacios_disponibles,
        context_list=contexts.espacios_disponibles,
        form=forms.BuscarFechaForm,
    )
