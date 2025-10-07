from django.contrib import admin

from .base import EmailAdmin
from ..models import email


@admin.register(email.CitasPacienteEmail)
class CitasCarnetEmailAdmin(EmailAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "correo_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(email.CitasColaboradorEmail)
class CitasColaboradorEmailAdmin(EmailAdmin):
    list_display = (
        "identificador",
        "mostrar_fecha_especificada",
        "correo_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(email.EspaciosVaciosEmail)
class EspaciosVaciosEmailAdmin(EmailAdmin):
    list_display = (
        "mostrar_fecha_especificada",
        "correo_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )
