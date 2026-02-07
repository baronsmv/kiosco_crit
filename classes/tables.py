from .selections import Table

cp = Table(name="cp", sql_expression="C_PACIENTE")
cu = Table(name="cu", sql_expression="C_USUARIO")
kpc = Table(name="kpc", sql_expression="K_PACIENTE_CITA")
kc = Table(name="kc", sql_expression="K_CITA")
cs = Table(name="cs", sql_expression="C_SERVICIO")
cc = Table(name="cc", sql_expression="C_CLINICA")
cec = Table(name="cec", sql_expression="C_ESTATUS_CITA")
ksd = Table(name="ksd", sql_expression="K_SERVICIO_DETALLE")
