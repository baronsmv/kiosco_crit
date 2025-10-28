from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import admin, menus, previews, search, send


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        route="whatsapp/admin/",
        view=user_passes_test(is_staff)(admin.whatsapp),
        name="admin_whatsapp",
    ),
    path(
        route="preview/excel/",
        view=previews.excel,
        name="preview_excel",
    ),
    path(
        route="preview/pdf/",
        view=previews.pdf,
        name="preview_pdf",
    ),
    path(
        route="send/whatsapp/pdf/",
        view=send.whatsapp_pdf,
        name="send_whatsapp_pdf",
    ),
    path(
        route="send/email/pdf/",
        view=send.email_pdf,
        name="send_email_pdf",
    ),
    path(
        route="paciente/datos/",
        view=search.datos_paciente,
        name="datos_paciente",
    ),
    path(
        route="paciente/citas/",
        view=search.citas_paciente,
        name="citas_paciente",
    ),
    path(
        route="colaborador/espacios/disponibles/",
        view=search.espacios_disponibles,
        name="espacios_disponibles",
    ),
    path(
        route="colaborador/citas/",
        view=search.citas_colaborador,
        name="citas_colaborador",
    ),
    path(route="paciente/", view=menus.paciente, name="menu_paciente"),
    path(route="colaborador/", view=menus.colaborador, name="menu_colaborador"),
    path(route="", view=menus.home, name="home"),
]
