from django.urls import path

from . import views

urlpatterns = [
    path(
        route="agendas/espacios/disponibles/",
        view=views.agenda_espacios_disponibles,
        name="agenda_espacios_disponibles",
    ),
    path(
        route="tablas/espacios/disponibles/",
        view=views.tabla_espacios_disponibles,
        name="tabla_espacios_disponibles",
    ),
]
