from django.contrib import admin

from .models import Consulta, EnvioWhatsapp, EnvioEmail


class BaseAdmin(admin.ModelAdmin):
    list_display = (
        "tipo",
        "identificador",
        "mostrar_fecha_especificada",
        "mostrar_destino",
        "mostrar_fecha_envio_o_consulta",
        "mostrar_ip_cliente",
        "estado",
    )
    list_filter = (
        "tipo",
        "fecha_especificada",
        "ip_cliente",
        "estado",
    )
    search_fields = ("identificador",)

    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"

    @admin.display(description="Fecha especificada", ordering="fecha_especificada")
    def mostrar_fecha_especificada(self, obj):
        return obj.fecha_especificada or "Fecha no especificada"

    def mostrar_destino(self, obj):
        return "-"

    def mostrar_fecha_envio_o_consulta(self, obj):
        return "-"


@admin.register(Consulta)
class ConsultaAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display
    list_filter = BaseAdmin.list_filter + ("fecha_consulta",)
    search_fields = BaseAdmin.search_fields + ("estado",)

    @admin.display(description="Fecha consulta", ordering="fecha_consulta")
    def mostrar_fecha_envio_o_consulta(self, obj):
        return obj.fecha_consulta


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
