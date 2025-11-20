from django.urls import path
from django.urls import register_converter

from classes.converters import DateConverter
from . import views

register_converter(DateConverter, "date")

urlpatterns = [
    path(
        route="api/paciente/datos/<str:id>/",
        view=views.api_datos_paciente,
        name="datos_paciente",
    ),
    path(
        route="api/paciente/citas/<str:id>/<date:fecha>/",
        view=views.api_citas_paciente,
        name="citas_paciente",
    ),
    path(
        route="api/paciente/citas/<str:id>/",
        view=views.api_citas_paciente,
        name="citas_paciente",
    ),
    path(
        route="api/espacios/disponibles/<date:fecha>/",
        view=views.api_espacios_disponibles,
        name="espacios_disponibles",
    ),
    path(
        route="api/espacios/disponibles/",
        view=views.api_espacios_disponibles,
        name="espacios_disponibles",
    ),
    path(
        route="api/colaborador/citas/<str:id>/<date:fecha>/",
        view=views.api_citas_colaborador,
        name="citas_colaborador",
    ),
    path(
        route="api/colaborador/citas/<str:id>/",
        view=views.api_citas_colaborador,
        name="citas_colaborador",
    ),
]
