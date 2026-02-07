from classes import tables
from classes.selections import SelectClause

nombre_paciente = SelectClause(
    name="Paciente",
    sql_name="nombre_paciente",
    sql_expression="CONCAT(cp.NB_PACIENTE,' ',cp.NB_PATERNO,' ',cp.NB_MATERNO)",
    table=tables.cp,
    format="name",
    required=True,
)
nombre_colaborador = SelectClause(
    name="Colaborador",
    sql_name="nombre_colaborador",
    sql_expression="CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO, ' ', cu.NB_MATERNO)",
    table=tables.cu,
    format="name",
    required=True,
)
no_carnet = SelectClause(
    name="Carnet",
    sql_name="no_carnet",
    sql_expression="cp.NO_CARNET",
    table=tables.cp,
    required=True,
)
nombre_usuario = SelectClause(
    name="Nombre de usuario",
    sql_name="nombre_usuario",
    sql_expression="cu.CL_LOGIN",
    table=tables.cu,
    required=True,
)
nombre_servicio = SelectClause(
    name="Servicio",
    sql_name="nombre_servicio",
    sql_expression="cs.NB_SERVICIO",
    table=tables.cs,
    required=True,
)
fecha_cita = SelectClause(
    name="Fecha y hora",
    sql_name="fecha_cita",
    sql_expression="FORMAT(kc.FE_CITA, 'dd/MM/yyyy HH:mm')",
    table=tables.kc,
    required=True,
)
clinica = SelectClause(
    name="Clínica",
    sql_name="clinica",
    sql_expression="cc.DS_CLINICA",
    table=tables.cc,
)
clinica_abrev = SelectClause(
    name="Clínica",
    sql_name="clinica_abrev",
    sql_expression="cc.NB_ABREVIADO",
    table=tables.cc,
)
estatus_cita = SelectClause(
    name="Estatus",
    sql_name="estatus_cita",
    sql_expression="cec.NB_ESTATUS_CITA",
    table=tables.cec,
)
espacios_disponibles = SelectClause(
    name="Disponibles",
    sql_name="espacios_disponibles",
    sql_expression="kc.NO_DISPONIBLES",
    table=tables.kc,
)
duracion_servicio = SelectClause(
    name="Duración",
    sql_name="duracion_servicio",
    sql_expression="CONCAT(kc.NO_DURACION,' min')",
    table=tables.kc,
)
inasistencias_paciente = SelectClause(
    name="Inasistencias",
    sql_name="inasistencias_paciente",
    sql_expression="cp.NO_INASISTENCIAS",
    table=tables.cp,
)
aniversario_paciente = SelectClause(
    name="Aniversario",
    sql_name="aniversario_paciente",
    sql_expression="FORMAT(cp.FE_ULTANIVERSARIO, 'dd/MM/yyyy')",
    table=tables.cp,
)
deuda_total_paciente = SelectClause(
    name="Deuda total",
    sql_name="deuda_total_paciente",
    sql_expression="FORMAT(SUM(ksd.MN_TOTAL - ksd.MN_PAGADO), '$#,##0.00', 'en-US')",
    table=tables.ksd,
)
