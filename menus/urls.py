from django.urls import path

from . import views, contexts

urlpatterns = [
    path(route="paciente/", view=views.paciente, name=contexts.paciente.url_name),
    path(
        route="colaborador/", view=views.colaborador, name=contexts.colaborador.url_name
    ),
    path(route="", view=views.home, name=contexts.inicio.url_name),
]
