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
    "citas": {
        "carnet": {
            "web": {
                "campos": [
                    "nb_servicio",
                    "fe_cita",
                    "nombre_colaborador",
                    "ds_clinica",
                    "estatus",
                ],
                "context": {
                    "title": "Búsqueda de citas",
                    "header": "Búsqueda de citas",
                    "form_label": "Número de Carnet:",
                    "form_placeholder": "Ej: 123456",
                    "date_label": "Fecha:",
                    "date_sublabel": "(Dejar vacío para mostrar todas)",
                    "button_label": "Buscar",
                    "data_title": "Datos del Paciente",
                    "table_title": "Citas",
                    "number_label": "Número telefónico:",
                    "send_button_label": "📤 Enviar por WhatsApp",
                },
            },
            "pdf": {
                "campos": [
                    "nb_servicio",
                    "fe_cita",
                    "nombre_colaborador",
                    "estatus",
                ],
                "context": {
                    "title": "Ficha del Paciente",
                    "header": "Ficha del Paciente",
                    "data_title": "Datos Personales",
                    "table_title": "Citas",
                    "footer": "Fundación Teletón México A.C.",
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
                        "sql": "FORMAT(kc.FE_CITA, 'dd/MM/yyyy hh:mm')",
                    },
                    "nombre_colaborador": {
                        "nombre": "Colaborador",
                        "sql": "CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO)",
                    },
                    "ds_clinica": {
                        "nombre": "Clínica",
                        "sql": "cc.DS_CLINICA",
                    },
                    "estatus": {
                        "nombre": "Estatus",
                        "sql": "cec.NB_ESTATUS_CITA",
                    },
                },
            },
        },
        "colaborador": {
            "web": {
                "campos": [
                    "nb_servicio",
                    "fe_cita",
                    "nombre_paciente",
                    "no_carnet",
                    "clinica_abrev",
                    "estatus",
                ],
                "context": {
                    "title": "Citas por Colaborador",
                    "header": "Citas por Colaborador",
                    "form_label": "Nombre de Usuario:",
                    "form_placeholder": "Ej: miguel.moedano",
                    "date_label": "Fecha:",
                    "date_sublabel": "(Dejar vacío para mostrar todas)",
                    "button_label": "Buscar",
                    "data_title": "Datos del Colaborador",
                    "table_title": "Citas del Día",
                    "number_label": "Número telefónico:",
                    "send_button_label": "📤 Enviar por WhatsApp",
                },
            },
            "pdf": {
                "campos": [
                    "nb_servicio",
                    "fe_cita",
                    "hora",
                    "nombre_paciente",
                    "no_carnet",
                ],
                "context": {
                    "title": "Agenda del Colaborador",
                    "header": "Agenda del Colaborador",
                    "data_title": "Datos del Colaborador",
                    "table_title": "Citas del Día",
                    "footer": "Fundación Teletón México A.C.",
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
                        "sql": "FORMAT(kc.FE_CITA, 'dd/MM/yyyy hh:mm')",
                    },
                    "nombre_paciente": {
                        "nombre": "Paciente",
                        "sql": "CONCAT(cp.NB_PACIENTE,' ',cp.NB_PATERNO,' ',cp.NB_MATERNO)",
                    },
                    "no_carnet": {
                        "nombre": "Carnet",
                        "sql": "cp.NO_CARNET",
                    },
                    "clinica_abrev": {
                        "nombre": "Clínica",
                        "sql": "cc.NB_ABREVIADO",
                    },
                    "estatus": {
                        "nombre": "Estatus",
                        "sql": "cec.NB_ESTATUS_CITA",
                    },
                },
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

cfg_whatsapp_admin = config.get("admin_whatsapp", {})

cfg_citas = config.get("citas", {})
cfg_citas_carnet = cfg_citas.get("carnet", {})
cfg_citas_colaborador = cfg_citas.get("colaborador", {})
