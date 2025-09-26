from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import (
    home,
    admin_whatsapp,
    vista_previa_pdf,
    buscar_citas_paciente,
    pdf_citas_paciente,
    buscar_citas_colaborador,
    pdf_citas_colaborador,
    buscar_espacios_disponibles,
    pdf_espacios_disponibles,
)


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        route="whatsapp/admin/",
        view=user_passes_test(is_staff)(admin_whatsapp),
        name="admin_whatsapp",
    ),
    path(
        route="pdf/<str:tipo>/<str:id>/",
        view=vista_previa_pdf,
        name="vista_previa_pdf",
    ),
    path(
        route="espacios/disponibles/pdf/<str:carnet>/",
        view=pdf_espacios_disponibles,
        name="pdf_espacios_disponibles",
    ),
    path(
        route="espacios/disponibles",
        view=buscar_espacios_disponibles,
        name="buscar_espacios_disponibles",
    ),
    path(
        route="citas/paciente/pdf/<str:carnet>/",
        view=pdf_citas_paciente,
        name="pdf_citas_paciente",
    ),
    path(
        route="citas/paciente",
        view=buscar_citas_paciente,
        name="buscar_citas_paciente",
    ),
    path(
        route="citas/colaborador/pdf/<str:id>/",
        view=pdf_citas_colaborador,
        name="pdf_citas_colaborador",
    ),
    path(
        route="citas/colaborador",
        view=buscar_citas_colaborador,
        name="buscar_citas_colaborador",
    ),
    path(route="", view=home, name="home"),
]
