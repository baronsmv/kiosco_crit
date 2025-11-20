from datetime import date
from typing import Optional

from django.http import HttpRequest, JsonResponse

from .utils import api_query_view
from .. import contexts, sql, selections


def api_citas_paciente(
    request: HttpRequest, id: str, fecha: Optional[date] = None
) -> JsonResponse:
    return api_query_view(
        request=request,
        context_list=contexts.citas_paciente,
        selection_list=selections.citas_paciente,
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
        context_list=contexts.datos_paciente,
        selection_list=selections.datos_paciente,
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
        context_list=contexts.citas_colaborador,
        selection_list=selections.citas_colaborador,
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
        context_list=contexts.citas_colaborador,
        selection_list=selections.citas_paciente,
        data_query=sql.data.espacios_disponibles,
        nombre_objetos="espacios disponibles",
        url_params={"fecha": fecha},
    )
