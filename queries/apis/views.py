from datetime import date
from typing import Optional

from django.http import HttpRequest, JsonResponse

from .utils import api_query_view
from .. import contexts
from ..sql import queries, selections


def api_citas_paciente(
    request: HttpRequest, id: str, fecha: Optional[date] = None
) -> JsonResponse:
    return api_query_view(
        request=request,
        context_list=contexts.citas_paciente,
        selection_list=selections.citas_paciente,
        data_query=queries.citas_paciente,
        url_params={"id": id, "fecha": fecha},
    )


def api_datos_paciente(request: HttpRequest, id: str) -> JsonResponse:
    return api_query_view(
        request=request,
        context_list=contexts.datos_paciente,
        selection_list=selections.datos_paciente,
        data_query=queries.datos_paciente,
        url_params={"id": id},
    )


def api_citas_colaborador(
    request: HttpRequest, id: str, fecha: Optional[date] = None
) -> JsonResponse:
    return api_query_view(
        request=request,
        context_list=contexts.citas_colaborador,
        selection_list=selections.citas_colaborador,
        data_query=queries.citas_colaborador,
        url_params={"id": id, "fecha": fecha},
    )


def api_espacios_disponibles(
    request: HttpRequest, fecha: date = date.today()
) -> JsonResponse:
    return api_query_view(
        request=request,
        context_list=contexts.espacios_disponibles,
        selection_list=selections.espacios_disponibles,
        data_query=queries.espacios_disponibles,
        url_params={"fecha": fecha},
    )
