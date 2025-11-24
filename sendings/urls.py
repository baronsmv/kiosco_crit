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
        route="send/whatsapp/",
        view=views.whatsapp,
        name="send_whatsapp",
    ),
    path(
        route="send/email/",
        view=views.email,
        name="send_email",
    ),
]
