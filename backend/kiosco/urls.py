from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import admin_whatsapp, buscar_citas_paciente, enviar_citas_paciente


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        "whatsapp/admin/",
        user_passes_test(is_staff)(admin_whatsapp),
        name="admin_whatsapp",
    ),
    path("", buscar_citas_paciente, name="buscar_paciente"),
    path(
        "enviar-pdf/<str:carnet>/",
        enviar_citas_paciente,
        name="enviar_pdf_whatsapp",
    ),
]
