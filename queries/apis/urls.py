from django.urls import path

from . import views

urlpatterns = [
    path(
        route="api/paciente/datos/",
        view=views.api_datos_paciente,
        name="datos_paciente",
    ),
    path(
        route="api/paciente/citas/",
        view=views.api_citas_paciente,
        name="citas_paciente",
    ),
    path(
        route="api/colaborador/espacios/disponibles/",
        view=views.api_espacios_disponibles,
        name="espacios_disponibles",
    ),
    path(
        route="api/colaborador/citas/",
        view=views.api_citas_colaborador,
        name="citas_colaborador",
    ),
]
