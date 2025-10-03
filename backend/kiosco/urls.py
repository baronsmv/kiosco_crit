from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import admin, menus, previews, search, send_pdf


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        route="whatsapp/admin/",
        view=user_passes_test(is_staff)(admin.whatsapp),
        name="admin_whatsapp",
    ),
    path(
        route="pdf/",
        view=previews.pdf,
        name="vista_previa_pdf",
    ),
    path(
        route="paciente/citas/pdf/",
        view=send_pdf.citas_paciente,
        name="pdf_citas_paciente",
    ),
    path(
        route="paciente/citas/",
        view=search.citas_paciente,
        name="buscar_citas_paciente",
    ),
    path(
        route="colaborador/espacios/disponibles/pdf/",
        view=send_pdf.espacios_disponibles,
        name="pdf_espacios_disponibles",
    ),
    path(
        route="colaborador/espacios/disponibles/",
        view=search.espacios_disponibles,
        name="buscar_espacios_disponibles",
    ),
    path(
        route="colaborador/citas/pdf/",
        view=send_pdf.citas_colaborador,
        name="pdf_citas_colaborador",
    ),
    path(
        route="colaborador/citas/",
        view=search.citas_colaborador,
        name="buscar_citas_colaborador",
    ),
    path(route="paciente/", view=menus.paciente, name="menu_paciente"),
    path(route="colaborador/", view=menus.colaborador, name="menu_colaborador"),
    path(route="", view=menus.home, name="home"),
]
