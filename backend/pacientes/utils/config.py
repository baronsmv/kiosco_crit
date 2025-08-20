from os import path
from typing import Dict

from yaml import dump, safe_load

CONFIG_FILE = "config.yml"

# Valores de configuración por defecto
default_config: Dict = {
    "admin_whatsapp": {
        "context": {
            "title": "Administración de WhatsApp",
            "header": "Administración de WhatsApp",
        }
    },
    "buscar_citas": {
        "webpage": {
            "campos": [
                "nb_servicio",
                "fe_cita",
                "nombre_colaborador",
                "ds_clinica",
                "cl_estatus_cita",
            ],
            "context": {
                "title": "Búsqueda de citas",
                "header": "Búsqueda de citas",
                "form_label": "Número de Carnet:",
                "form_placeholder": "Ej: 123456",
                "button_label": "Buscar",
                "date_label": "Fecha:",
                "send_button_label": "📤 Enviar por WhatsApp",
                "tabla_titulo": "Citas",
            },
        },
        "pdf": {
            "campos": [
                "nb_servicio",
                "fe_cita",
                "nombre_colaborador",
                "cl_estatus_cita",
            ],
            "context": {
                "tabla_titulo": "Citas",
            },
        },
        "sql": {
            "campos": {
                "nb_servicio": {
                    "nombre": "Servicio",
                    "sql": "cs.NB_SERVICIO",
                },
                "fe_cita": {
                    "nombre": "Fecha y hora",
                    "sql": "kc.FE_CITA",
                    "tipo": "fecha",
                },
                "nombre_colaborador": {
                    "nombre": "Colaborador",
                    "sql": "CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO)",
                },
                "ds_clinica": {
                    "nombre": "Clínica",
                    "sql": "cc.DS_CLINICA",
                },
                "cl_estatus_cita": {
                    "nombre": "Estatus",
                    "sql": "kpc.CL_ESTATUS_CITA",
                    "tipo": "estatus",
                },
            },
            "mapeo_estatus": {
                "A": "Activo",
                "I": "Inasistencia",
                "P": "Pospuesta",
                "T": "Tomada",
            },
        },
    },
}

# Si no existe el archivo, crear uno con valores por defecto
config: Dict = {}
if not path.exists(CONFIG_FILE):
    print(
        f"Aviso: No se encontró el archivo de configuración: {CONFIG_FILE}. Se usarán valores por defecto."
    )
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        dump(default_config, f, allow_unicode=True)
    config = default_config
else:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = safe_load(f) or {}

whatsapp_admin = config.get("admin_whatsapp", {})
citas_web = config.get("buscar_citas", {}).get("webpage", {})
citas_pdf = config.get("buscar_citas", {}).get("pdf", {})
citas_sql = config.get("buscar_citas", {}).get("sql", {})
