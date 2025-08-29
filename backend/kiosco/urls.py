from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import admin_whatsapp, buscar_citas_por_carnet, enviar_citas_por_carnet


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        "whatsapp/admin/",
        user_passes_test(is_staff)(admin_whatsapp),
        name="admin_whatsapp",
    ),
    path("", buscar_citas_por_carnet, name="buscar_paciente"),
    path(
        "pdf-citas-carnet/<str:carnet>/",
        enviar_citas_por_carnet,
        name="pdf_citas_carnet",
    ),
]
