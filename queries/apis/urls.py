from django.urls import path

from .views import (
    CitasPaciente,
    DatosPaciente,
    CitasColaborador,
    EspaciosDisponibles,
)

urlpatterns = [
    path("api/paciente/citas", CitasPaciente.as_view(), name="api_paciente_citas"),
    path("api/paciente/datos", DatosPaciente.as_view(), name="api_paciente_datos"),
    path(
        "api/colaborador/citas",
        CitasColaborador.as_view(),
        name="api_colaborador_citas",
    ),
    path(
        "api/espacios/disponibles/",
        EspaciosDisponibles.as_view(),
        name="api_espacios_disponibles",
    ),
]
