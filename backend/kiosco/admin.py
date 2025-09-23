from django.contrib import admin

from .models import (
    CitasCarnetConsulta,
    CitasCarnetWhatsapp,
    CitasColaboradorConsulta,
    CitasColaboradorWhatsapp,
)


class BaseAdmin(admin.ModelAdmin):
    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"

    @admin.display(description="Fecha especificada", ordering="fecha_especificada")
    def mostrar_fecha_especificada(self, obj):
        return obj.fecha_especificada or "Fecha no especificada"


class BaseConsultaAdmin(BaseAdmin):
    list_filter = ("fecha_especificada", "fecha_consulta", "ip_cliente", "estado")
    search_fields = ("identificador",)


class BaseWhatsappAdmin(BaseAdmin):
    list_filter = ("fecha_especificada", "fecha_envio", "ip_cliente", "estado")
    search_fields = ("identificador", "numero_destino")


@admin.register(CitasCarnetConsulta)
class CitasCarnetConsultaAdmin(BaseConsultaAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(CitasCarnetWhatsapp)
class CitasCarnetWhatsappAdmin(BaseWhatsappAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "numero_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(CitasColaboradorConsulta)
class CitasColaboradorConsultaAdmin(BaseConsultaAdmin):
    list_display = (
        "identificador",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(CitasColaboradorWhatsapp)
class CitasColaboradorWhatsappAdmin(BaseWhatsappAdmin):
    list_display = (
        "identificador",
        "mostrar_fecha_especificada",
        "numero_destino",
        "fecha_envio",
        "mostrar_ip_cliente",
        "estado",
    )
