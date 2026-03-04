from django.urls import path

from menus import contexts
from . import views

urlpatterns = [
    path(
        route="agendas/espacios/disponibles/",
        view=views.agenda_espacios_disponibles,
        name=contexts.agenda_espacios_disponibles.url_name,
    ),
    path(
        route="tablas/espacios/disponibles/",
        view=views.tabla_espacios_disponibles,
        name=contexts.tabla_espacios_disponibles.url_name,
    ),
]
