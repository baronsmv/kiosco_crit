from django.urls import path

from . import views

urlpatterns = [
    path(route="paciente/", view=views.paciente, name="menu_paciente"),
    path(route="colaborador/", view=views.colaborador, name="menu_colaborador"),
    path(route="", view=views.home, name="home"),
]
