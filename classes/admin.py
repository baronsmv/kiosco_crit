from django.contrib import admin


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
