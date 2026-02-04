from django.contrib import admin

from classes.admin import BaseAdmin
from .models import Consulta


@admin.register(Consulta)
class ConsultaAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display
    list_filter = BaseAdmin.list_filter + ("fecha_consulta",)
    search_fields = BaseAdmin.search_fields + ("identificador",)

    @admin.display(description="Identificador", ordering="identificador")
    def mostrar_destino(self, obj):
        return obj.identificador or "-"

    @admin.display(description="Fecha consulta", ordering="fecha_consulta")
    def mostrar_fecha_envio_o_consulta(self, obj):
        return obj.fecha_consulta or "-"
