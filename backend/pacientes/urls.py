from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import admin_whatsapp, buscar_paciente, enviar_pdf_whatsapp


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        "whatsapp/admin/",
        user_passes_test(is_staff)(admin_whatsapp),
        name="admin_whatsapp",
    ),
    path("", buscar_paciente, name="buscar_paciente"),
    path(
        "enviar-pdf/<str:carnet>/<str:fecha>/",
        enviar_pdf_whatsapp,
        name="enviar_pdf_whatsapp",
    ),
]
