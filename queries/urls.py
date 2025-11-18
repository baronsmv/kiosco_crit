from django.urls import path

from . import views

urlpatterns = [
    path(
        route="paciente/datos/",
        view=views.datos_paciente,
        name="datos_paciente",
    ),
    path(
        route="paciente/citas/",
        view=views.citas_paciente,
        name="citas_paciente",
    ),
    path(
        route="espacios/disponibles/",
        view=views.espacios_disponibles,
        name="espacios_disponibles",
    ),
    path(
        route="colaborador/citas/",
        view=views.citas_colaborador,
        name="citas_colaborador",
    ),
]
