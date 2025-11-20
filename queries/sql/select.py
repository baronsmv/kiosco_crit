from dataclasses import dataclass


@dataclass(frozen=True)
class Select:
    nombre: str
    sql: str
    formatear: str | None = None


nombre_paciente = Select(
    nombre="Paciente",
    sql="CONCAT(cp.NB_PACIENTE,' ',cp.NB_PATERNO,' ',cp.NB_MATERNO)",
    formatear="nombre",
)
nombre_colaborador = Select(
    nombre="Colaborador",
    sql="CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO, ' ', cu.NB_MATERNO)",
    formatear="nombre",
)
no_carnet = Select(
    nombre="Carnet",
    sql="cp.NO_CARNET",
)
nombre_servicio = Select(
    nombre="Servicio",
    sql="cs.NB_SERVICIO",
)
fecha_cita = Select(
    nombre="Fecha y hora",
    sql="FORMAT(kc.FE_CITA, 'dd/MM/yyyy HH:mm')",
)
clinica = Select(
    nombre="Clínica",
    sql="cc.DS_CLINICA",
)
clinica_abrev = Select(
    nombre="Clínica",
    sql="cc.NB_ABREVIADO",
)
estatus_cita = Select(
    nombre="Estatus",
    sql="cec.NB_ESTATUS_CITA",
)
espacios_disponibles = Select(
    nombre="Disponibles",
    sql="kc.NO_DISPONIBLES",
)
duracion_servicio = Select(
    nombre="Duración",
    sql="CONCAT(kc.NO_DURACION,' min')",
)
inasistencias_paciente = Select(
    nombre="Inasistencias",
    sql="CP.NO_INASISTENCIAS",
)
aniversario_paciente = Select(
    nombre="Aniversario",
    sql="CP.FE_ULTANIVERSARIO",
)
deuda_total_paciente = Select(
    nombre="Deuda total",
    sql="CONVERT(DECIMAL(10,2), SUM(KSD.MN_TOTAL - KSD.MN_PAGADO))",
)
