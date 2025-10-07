from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import admin, menus, previews, search, send_email, send_whatsapp


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        route="whatsapp/admin/",
        view=user_passes_test(is_staff)(admin.whatsapp),
        name="admin_whatsapp",
    ),
    path(
        route="preview/pdf",
        view=previews.pdf,
        name="preview_pdf",
    ),
    path(
        route="paciente/citas/send/whatsapp/pdf/",
        view=send_whatsapp.pdf_citas_paciente,
        name="send_email_pdf_citas_paciente",
    ),
    path(
        route="paciente/citas/send/email/pdf/",
        view=send_email.pdf_citas_paciente,
        name="send_email_pdf_citas_paciente",
    ),
    path(
        route="paciente/citas/",
        view=search.citas_paciente,
        name="buscar_citas_paciente",
    ),
    path(
        route="colaborador/espacios/disponibles/send/whatsapp/pdf/",
        view=send_whatsapp.pdf_espacios_disponibles,
        name="send_whatsapp_pdf_espacios_disponibles",
    ),
    path(
        route="colaborador/espacios/disponibles/send/email/pdf/",
        view=send_email.pdf_espacios_disponibles,
        name="send_email_pdf_espacios_disponibles",
    ),
    path(
        route="colaborador/espacios/disponibles/",
        view=search.espacios_disponibles,
        name="buscar_espacios_disponibles",
    ),
    path(
        route="colaborador/citas/send/whatsapp/pdf/",
        view=send_whatsapp.pdf_citas_colaborador,
        name="send_whatsapp_pdf_citas_colaborador",
    ),
    path(
        route="colaborador/citas/send/email/pdf/",
        view=send_email.pdf_citas_colaborador,
        name="send_email_pdf_citas_colaborador",
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
