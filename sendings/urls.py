from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from . import views


def is_staff(user):
    return user.is_staff


urlpatterns = [
    path(
        route="whatsapp/admin/",
        view=user_passes_test(is_staff)(views.whatsapp_admin),
        name="admin_whatsapp",
    ),
    path(
        route="send/whatsapp/pdf/",
        view=views.whatsapp_pdf,
        name="send_whatsapp_pdf",
    ),
    path(
        route="send/email/pdf/",
        view=views.email_pdf,
        name="send_email_pdf",
    ),
]
