from django.contrib import admin

from .models import EnvioWhatsApp


@admin.register(EnvioWhatsApp)
class EnvioWhatsAppAdmin(admin.ModelAdmin):
    list_display = ("paciente", "numero_destino", "estado", "fecha_envio")
    list_filter = ("estado", "fecha_envio")
    search_fields = ("paciente__nombre", "numero_destino")
