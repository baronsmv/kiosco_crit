from classes.selections import SelectClause

nombre_paciente = SelectClause(
    name="Paciente",
    sql_name="nombre_paciente",
    sql_expression="CONCAT(cp.NB_PACIENTE,' ',cp.NB_PATERNO,' ',cp.NB_MATERNO)",
    format="name",
)
nombre_colaborador = SelectClause(
    name="Colaborador",
    sql_name="nombre_colaborador",
    sql_expression="CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO, ' ', cu.NB_MATERNO)",
    format="name",
)
no_carnet = SelectClause(
    name="Carnet",
    sql_name="no_carnet",
    sql_expression="cp.NO_CARNET",
)
nombre_servicio = SelectClause(
    name="Servicio",
    sql_name="nombre_servicio",
    sql_expression="cs.NB_SERVICIO",
)
fecha_cita = SelectClause(
    name="Fecha y hora",
    sql_name="fecha_cita",
    sql_expression="FORMAT(kc.FE_CITA, 'dd/MM/yyyy HH:mm')",
)
clinica = SelectClause(
    name="Clínica",
    sql_name="clinica",
    sql_expression="cc.DS_CLINICA",
)
clinica_abrev = SelectClause(
    name="Clínica",
    sql_name="clinica_abrev",
    sql_expression="cc.NB_ABREVIADO",
)
estatus_cita = SelectClause(
    name="Estatus",
    sql_name="estatus_cita",
    sql_expression="cec.NB_ESTATUS_CITA",
)
espacios_disponibles = SelectClause(
    name="Disponibles",
    sql_name="espacios_disponibles",
    sql_expression="kc.NO_DISPONIBLES",
)
duracion_servicio = SelectClause(
    name="Duración",
    sql_name="duracion_servicio",
    sql_expression="CONCAT(kc.NO_DURACION,' min')",
)
inasistencias_paciente = SelectClause(
    name="Inasistencias",
    sql_name="inasistencias_paciente",
    sql_expression="CP.NO_INASISTENCIAS",
)
aniversario_paciente = SelectClause(
    name="Aniversario",
    sql_name="aniversario_paciente",
    sql_expression="FORMAT(CP.FE_ULTANIVERSARIO, 'dd/MM/yyyy')",
)
deuda_total_paciente = SelectClause(
    name="Deuda total",
    sql_name="deuda_total_paciente",
    sql_expression="STR(SUM(KSD.MN_TOTAL - KSD.MN_PAGADO), 10, 2)",
)
