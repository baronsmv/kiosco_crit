from django.urls import path

from . import views

urlpatterns = [
    path(
        route="agendas/espacios/disponibles/",
        view=views.agenda_espacios_disponibles,
        name="agenda_espacios_disponibles",
    ),
]
