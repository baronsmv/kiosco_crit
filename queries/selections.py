from classes.selections import SelectionList
from .sql import select

citas_paciente = SelectionList(
    web=(
        select.nombre_servicio,
        select.fecha_cita,
        select.nombre_colaborador,
        select.clinica,
        select.estatus_cita,
    ),
    pdf=(
        select.nombre_servicio,
        select.fecha_cita,
        select.nombre_colaborador,
        select.estatus_cita,
    ),
)

datos_paciente = SelectionList(
    web=(
        select.no_carnet,
        select.nombre_paciente,
        select.clinica,
        select.inasistencias_paciente,
        select.aniversario_paciente,
        select.deuda_total_paciente,
    ),
)

citas_colaborador = SelectionList(
    web=(
        select.nombre_servicio,
        select.fecha_cita,
        select.nombre_paciente,
        select.no_carnet,
        select.clinica_abrev,
        select.estatus_cita,
    ),
)

espacios_disponibles = SelectionList(
    web=(
        select.nombre_servicio,
        select.fecha_cita,
        select.nombre_colaborador,
        select.espacios_disponibles,
        select.duracion_servicio,
    ),
)
