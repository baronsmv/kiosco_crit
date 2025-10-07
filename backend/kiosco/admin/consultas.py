from django.contrib import admin

from .base import ConsultaAdmin
from ..models import consultas


@admin.register(consultas.CitasPaciente)
class CitasPacienteConsultaAdmin(ConsultaAdmin):
    list_display = (
        "carnet",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
        "estado",
    )


@admin.register(consultas.CitasColaborador)
class CitasColaboradorConsultaAdmin(ConsultaAdmin):
    list_display = (
        "identificador",
        "mostrar_fecha_especificada",
        "fecha_consulta",
        "mostrar_ip_cliente",
        "estado",
    )
