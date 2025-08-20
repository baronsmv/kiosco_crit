from django.contrib import admin

from .models import CitasConsulta, CitasWhatsapp


@admin.register(CitasConsulta)
class CitasConsulta(admin.ModelAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
    )
    list_filter = ("fecha_especificada", "fecha_consulta", "ip_cliente")
    search_fields = ("carnet",)

    @admin.display(description="Fecha especificada", ordering="fecha_especificada")
    def mostrar_fecha_especificada(self, obj):
        return obj.fecha_especificada or "Fecha no especificada"

    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"


@admin.register(CitasWhatsapp)
class CitasWhatsApp(admin.ModelAdmin):
    list_display = (
        "carnet",
        "numero_destino",
        "estado",
        "fecha_envio",
        "mostrar_ip_cliente",
    )
    list_filter = ("estado", "fecha_envio", "ip_cliente")
    search_fields = ("carnet", "numero_destino")

    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"
