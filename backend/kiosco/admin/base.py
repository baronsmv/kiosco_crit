from django.contrib import admin


class Admin(admin.ModelAdmin):
    @admin.display(description="IP de cliente", ordering="ip_cliente")
    def mostrar_ip_cliente(self, obj):
        return obj.ip_cliente or "IP no identificada"

    @admin.display(description="Fecha especificada", ordering="fecha_especificada")
    def mostrar_fecha_especificada(self, obj):
        return obj.fecha_especificada or "Fecha no especificada"


class ConsultaAdmin(Admin):
    list_filter = ("fecha_especificada", "fecha_consulta", "ip_cliente", "estado")
    search_fields = ("identificador",)


class WhatsappAdmin(Admin):
    list_filter = ("fecha_especificada", "fecha_envio", "ip_cliente", "estado")
    search_fields = ("identificador", "numero_destino")


class EmailAdmin(Admin):
    list_filter = ("fecha_especificada", "fecha_envio", "ip_cliente", "estado")
    search_fields = ("identificador", "correo_destino")
