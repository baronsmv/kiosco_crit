from django.contrib import admin

from .models import (
    CitasCarnetConsulta,
    CitasCarnetWhatsapp,
    CitasColaboradorConsulta,
    CitasColaboradorWhatsapp,
)


class BaseConsultaAdmin(admin.ModelAdmin):
    list_filter = ("fecha_especificada", "fecha_consulta", "ip_cliente")
    search_fields = ("identificador",)

    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"

    @admin.display(description="Fecha especificada", ordering="fecha_especificada")
    def mostrar_fecha_especificada(self, obj):
        return obj.fecha_especificada or "Fecha no especificada"


class BaseWhatsappAdmin(admin.ModelAdmin):
    list_filter = ("estado", "fecha_envio", "ip_cliente")
    search_fields = ("identificador", "numero_destino")

    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"


@admin.register(CitasCarnetConsulta)
class CitasCarnetConsultaAdmin(BaseConsultaAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
    )


@admin.register(CitasCarnetWhatsapp)
class CitasCarnetWhatsappAdmin(BaseWhatsappAdmin):
    list_display = (
        "carnet",
        "numero_destino",
        "estado",
        "fecha_envio",
        "mostrar_ip_cliente",
    )


@admin.register(CitasColaboradorConsulta)
class CitasColaboradorConsultaAdmin(BaseConsultaAdmin):
    list_display = (
        "identificador",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
    )


@admin.register(CitasColaboradorWhatsapp)
class CitasColaboradorWhatsappAdmin(BaseWhatsappAdmin):
    list_display = (
        "identificador",
        "numero_destino",
        "estado",
        "fecha_envio",
        "mostrar_ip_cliente",
    )
