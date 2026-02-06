from .selections import Join
from . import tables

cp_kpc = Join(
    left=tables.CP,
    right=tables.KPC,
    on="FL_PACIENTE"
)
cu_kc = Join(
    left=tables.CU,
    right=tables.KC,
    on="FL_USUARIO"
)
kpc_kc = Join(
    left=tables.KPC,
    right=tables.KC,
    on="FL_CITA"
)
kc_cs = Join(
    left=tables.KC,
    right=tables.CS,
    on="FL_SERVICIO"
)
kc_cu = Join(
    left=tables.KC,
    right=tables.CU,
    on="FL_USUARIO"
)
cp_cc = Join(
    left=tables.CP,
    right=tables.CC,
    on="FL_CLINICA"
)
kpc_cec = Join(
    left=tables.KPC,
    right=tables.CEC,
    on="CL_ESTATUS_CITA"
)
kpc_ksd = Join(
    left=tables.KPC,
    right=tables.KSD,
    on="FL_PACIENTE_CITA"
)
