from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from .views import (
    admin_whatsapp,
    buscar_citas_carnet,
    pdf_citas_carnet,
    buscar_citas_colaborador,
    pdf_citas_colaborador,
    vista_previa_pdf,
    home,
)


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        "whatsapp/admin/",
        user_passes_test(is_staff)(admin_whatsapp),
        name="admin_whatsapp",
    ),
    path(
        "pdf/<str:tipo>/<str:id>/",
        vista_previa_pdf,
        name="vista_previa_pdf",
    ),
    path(
        "citas/carnet/pdf/<str:carnet>/",
        pdf_citas_carnet,
        name="pdf_citas_carnet",
    ),
    path(
        "citas/carnet",
        buscar_citas_carnet,
        name="buscar_citas_carnet",
    ),
    path(
        "citas/colaborador/pdf/<str:id>/",
        pdf_citas_colaborador,
        name="pdf_citas_colaborador",
    ),
    path(
        "citas/colaborador",
        buscar_citas_colaborador,
        name="buscar_citas_colaborador",
    ),
    path("", home, name="home"),
]
