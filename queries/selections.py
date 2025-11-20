from dataclasses import dataclass
from typing import Tuple

from .sql import select
from .sql.select import Select

SubSelection = Tuple[Select, ...]


@dataclass(frozen=True)
class Selection:
    web: SubSelection
    subject: SubSelection = ()
    api: SubSelection = ()
    pdf: SubSelection = ()
    excel: SubSelection = ()
    sql: SubSelection = ()

    def __post_init__(self):
        merged = {
            select
            for sub in (self.web, self.subject, self.api, self.pdf, self.excel)
            for select in sub
        }
        object.__setattr__(self, "sql", tuple(merged))

        for field_name in ("api", "pdf", "excel"):
            if not getattr(self, field_name):
                object.__setattr__(self, field_name, self.web)


citas_paciente = Selection(
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

datos_paciente = Selection(
    web=(
        select.no_carnet,
        select.nombre_paciente,
        select.clinica,
        select.inasistencias_paciente,
        select.aniversario_paciente,
        select.deuda_total_paciente,
    ),
)

citas_colaborador = Selection(
    web=(
        select.nombre_servicio,
        select.fecha_cita,
        select.nombre_paciente,
        select.no_carnet,
        select.clinica_abrev,
        select.estatus_cita,
    ),
)

espacios_disponibles = Selection(
    web=(
        select.nombre_servicio,
        select.fecha_cita,
        select.nombre_colaborador,
        select.espacios_disponibles,
        select.duracion_servicio,
    ),
)
