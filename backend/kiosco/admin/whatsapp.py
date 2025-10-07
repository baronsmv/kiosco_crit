from django.contrib import admin

from .base import WhatsappAdmin
from ..models import whatsapp


@admin.register(whatsapp.CitasCarnetWA)
class CitasCarnetWAAdmin(WhatsappAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "numero_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(whatsapp.CitasColaboradorWA)
class CitasColaboradorWAAdmin(WhatsappAdmin):
    list_display = (
        "identificador",
        "mostrar_fecha_especificada",
        "numero_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )
