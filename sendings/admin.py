from django.contrib import admin

from classes.admin import BaseAdmin
from .models import EnvioWhatsapp, EnvioEmail


@admin.register(EnvioWhatsapp)
class EnvioWhatsappAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display
    list_filter = BaseAdmin.list_filter + ("fecha_envio",)
    search_fields = BaseAdmin.search_fields + ("numero_destino",)

    @admin.display(description="Número destino", ordering="numero_destino")
    def mostrar_destino(self, obj):
        return obj.numero_destino

    @admin.display(description="Fecha envío", ordering="fecha_envio")
    def mostrar_fecha_envio_o_consulta(self, obj):
        return obj.fecha_envio


@admin.register(EnvioEmail)
class EnvioEmailAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display
    list_filter = BaseAdmin.list_filter + ("fecha_envio",)
    search_fields = BaseAdmin.search_fields + ("correo_destino",)

    @admin.display(description="Correo destino", ordering="correo_destino")
    def mostrar_destino(self, obj):
        return obj.correo_destino

    @admin.display(description="Fecha envío", ordering="fecha_envio")
    def mostrar_fecha_envio_o_consulta(self, obj):
        return obj.fecha_envio
