from classes.selections import SelectionList
from queries.sql import select

paciente = (select.nombre_paciente, select.no_carnet)
colaborador = (select.nombre_colaborador, select.nombre_usuario)

citas_paciente = SelectionList(
    subject=paciente,
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
    subject=(
        select.no_carnet,
        select.nombre_paciente,
        select.clinica,
        select.inasistencias_paciente,
        select.aniversario_paciente,
        select.deuda_total_paciente,
    ),
)

citas_colaborador = SelectionList(
    subject=colaborador,
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
