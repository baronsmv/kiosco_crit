from . import tables
from .selections import Join

cp_kpc = Join(left=tables.cp, right=tables.kpc, on="FL_PACIENTE")
cp_cc = Join(left=tables.cp, right=tables.cc, on="FL_CLINICA")

cu_kc = Join(left=tables.cu, right=tables.kc, on="FL_USUARIO")
kc_kpc = Join(left=tables.kc, right=tables.kpc, on="FL_CITA")

kpc_kc = Join(left=tables.kpc, right=tables.kc, on="FL_CITA")
kpc_cec = Join(left=tables.kpc, right=tables.cec, on="CL_ESTATUS_CITA")
kpc_ksd = Join(left=tables.kpc, right=tables.ksd, on="FL_PACIENTE_CITA")

kpc_cp = Join(left=tables.kpc, right=tables.cp, on="FL_PACIENTE")

kc_cs = Join(left=tables.kc, right=tables.cs, on="FL_SERVICIO")
kc_cu = Join(left=tables.kc, right=tables.cu, on="FL_USUARIO")
