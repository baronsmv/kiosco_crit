from django.urls import path

from menus import contexts
from . import views

urlpatterns = [
    path(
        route="paciente/citas/",
        view=views.citas_paciente,
        name=contexts.citas_paciente.url_name,
    ),
    path(
        route="paciente/prescripciones/",
        view=views.prescripciones_paciente,
        name=contexts.prescripciones_paciente.url_name,
    ),
    path(
        route="paciente/datos/",
        view=views.datos_paciente,
        name=contexts.datos_paciente.url_name,
    ),
    path(
        route="espacios/disponibles/",
        view=views.espacios_disponibles,
        name=contexts.espacios_disponibles.url_name,
    ),
    path(
        route="colaborador/citas/",
        view=views.citas_colaborador,
        name=contexts.citas_colaborador.url_name,
    ),
]
