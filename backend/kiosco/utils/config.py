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
    "menús": {
        "inicio": {
            "context": {
                "title": "Kiosco de Información",
                "header": "Kiosco de Información",
                "select_text": "Selecciona una opción para continuar:",
                "mostrar_inicio": False,
            },
            "options": {
                "menu_paciente": {
                    "title": "👤 Pacientes",
                    "description": "Información relevante para pacientes.",
                },
                "menu_colaborador": {
                    "title": "👤 Colaboradores",
                    "description": "Información relevante para colaboradores.",
                },
            },
        },
        "paciente": {
            "context": {
                "title": "Kiosco de Información",
                "header": "Información para Pacientes",
                "select_text": "Selecciona una opción para continuar:",
                "mostrar_inicio": True,
                "home_label": "Inicio",
            },
            "options": {
                "buscar_citas_paciente": {
                    "title": "🪪 Citas por Paciente",
                    "description": "Busca citas con el carnet de un paciente.",
                },
            },
        },
        "colaborador": {
            "context": {
                "title": "Kiosco de Información",
                "header": "Información para Colaboradores",
                "select_text": "Selecciona una opción para continuar:",
                "mostrar_inicio": True,
                "home_label": "Inicio",
            },
            "options": {
                "buscar_citas_colaborador": {
                    "title": "👤 Citas por Colaborador",
                    "description": "Busca citas de un colaborador.",
                },
                "buscar_espacios_disponibles": {
                    "title": "📅 Espacios disponibles",
                    "description": "Busca espacios disponibles para agendar.",
                },
            },
        },
    },
    "common_resources": {
        "sql": {
            "campos": {
                "nombre_paciente": {
                    "nombre": "Paciente",
                    "sql": "CONCAT(cp.NB_PACIENTE,' ',cp.NB_PATERNO,' ',cp.NB_MATERNO)",
                    "formatear": "nombre",
                },
                "nombre_colaborador": {
                    "nombre": "Colaborador",
                    "sql": "CONCAT(cu.NB_USUARIO, ' ', cu.NB_PATERNO, ' ', cu.NB_MATERNO)",
                    "tipo": "nombre",
                },
                "no_carnet": {
                    "nombre": "Carnet",
                    "sql": "cp.NO_CARNET",
                },
                "nombre_servicio": {
                    "nombre": "Servicio",
                    "sql": "cs.NB_SERVICIO",
                },
                "fecha_cita": {
                    "nombre": "Fecha y hora",
                    "sql": "FORMAT(kc.FE_CITA, 'dd/MM/yyyy HH:mm')",
                },
                "clinica": {
                    "nombre": "Clínica",
                    "sql": "cc.DS_CLINICA",
                },
                "clinica_abrev": {
                    "nombre": "Clínica",
                    "sql": "cc.NB_ABREVIADO",
                },
                "estatus_cita": {
                    "nombre": "Estatus",
                    "sql": "cec.NB_ESTATUS_CITA",
                },
                "espacios_disponibles": {
                    "nombre": "Espacios disponibles",
                    "sql": "kc.NO_DISPONIBLES",
                },
                "duracion_servicio": {
                    "nombre": "Duración de servicio",
                    "sql": "CONCAT(kc.NO_DURACION,' min')",
                },
            },
        },
    },
    "citas": {
        "carnet": {
            "web": {
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "clinica",
                    "estatus_cita",
                ],
                "filtros": {
                    "kpc.CL_ESTATUS_CITA": {
                        "con_fecha": ["A", "N"],
                        "sin_fecha": ["A"],
                    },
                },
                "context": {
                    "title": "Búsqueda de citas",
                    "header": "Búsqueda de citas",
                    "id_label": "Número de Carnet:",
                    "id_placeholder": "Ej: 123456",
                    "id_required": True,
                    "date_label": "Fecha:",
                    "date_sublabel": "(Dejar vacío para mostrar todas)",
                    "date_required": False,
                    "button_label": "Buscar",
                    "processing_message": "Procesando...",
                    "data_title": "Datos del Paciente",
                    "table_title": "Citas",
                    "number_label": "Número telefónico:",
                    "preview_label": "Vista previa e impresión",
                    "send_button_label": "📤 Enviar por WhatsApp",
                    "home_label": "Inicio",
                    "fecha_inicial": False,
                    "auto_borrado": True,
                    "mostrar_imprimir": True,
                    "mostrar_inicio": True,
                    "id_pattern": r"[a-zA-Z0-9. -]+",
                    "id_max_length": 20,
                },
            },
            "pdf": {
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "estatus_cita",
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
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "clinica",
                    "estatus_cita",
                ],
            },
        },
        "colaborador": {
            "web": {
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_paciente",
                    "no_carnet",
                    "clinica_abrev",
                    "estatus_cita",
                ],
                "context": {
                    "title": "Citas por Colaborador",
                    "header": "Citas por Colaborador",
                    "id_label": "Nombre de Usuario:",
                    "id_placeholder": "Ej: miguel.moedano",
                    "id_required": True,
                    "date_label": "Fecha:",
                    "date_sublabel": "(Dejar vacío para mostrar todas)",
                    "date_required": False,
                    "button_label": "Buscar",
                    "processing_message": "Procesando...",
                    "data_title": "Datos del Colaborador",
                    "table_title": "Citas del Día",
                    "number_label": "Número telefónico:",
                    "preview_label": "Vista previa e impresión",
                    "send_button_label": "📤 Enviar por WhatsApp",
                    "home_label": "Inicio",
                    "fecha_inicial": True,
                    "auto_borrado": False,
                    "mostrar_imprimir": True,
                    "mostrar_inicio": True,
                    "id_pattern": r"[a-zA-Z0-9. -]+",
                    "id_max_length": 20,
                },
            },
            "pdf": {
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_paciente",
                    "no_carnet",
                    "clinica_abrev",
                    "estatus_cita",
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
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_paciente",
                    "no_carnet",
                    "clinica_abrev",
                    "estatus_cita",
                ],
            },
        },
    },
    "espacios": {
        "web": {
            "campos": [
                "nombre_servicio",
                "fecha_cita",
                "no_carnet",
                "clinica_abrev",
                "estatus_cita",
            ],
            "context": {
                "title": "Espacios Disponibles",
                "header": "Espacios Disponibles",
                "date_label": "Fecha:",
                "date_required": True,
                "button_label": "Buscar",
                "processing_message": "Procesando...",
                "data_title": "Espacios Disponibles",
                "table_title": "Espacios Disponibles",
                "number_label": "Número telefónico:",
                "preview_label": "Vista previa e impresión",
                "send_button_label": "📤 Enviar por WhatsApp",
                "home_label": "Inicio",
                "fecha_inicial": True,
                "auto_borrado": False,
                "mostrar_imprimir": True,
                "mostrar_inicio": True,
            },
        },
        "pdf": {
            "campos": [
                "nombre_servicio",
                "fecha_cita",
                "no_carnet",
                "clinica_abrev",
                "estatus_cita",
            ],
            "context": {
                "title": "Espacios Disponibles",
                "header": "Espacios Disponibles",
                "data_title": "Espacios Disponibles",
                "table_title": "Espacios Disponibles",
                "footer": "Fundación Teletón México A.C.",
            },
        },
        "sql": {
            "campos": [
                "nombre_servicio",
                "fecha_cita",
                "nombre_colaborador",
                "espacios_disponibles",
                "duracion_servicio",
            ],
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
        dump(default_config, f, allow_unicode=True, sort_keys=False)
    config = default_config
else:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = safe_load(f) or {}


def parse_campos(
    config: Dict,
    common: Dict[str, str] = config["common_resources"]["sql"]["campos"],
) -> Dict:
    if "sql" not in config or "campos" not in config["sql"]:
        return config
    config["sql"]["campos"] = {k: common[k] for k in config["sql"]["campos"]}
    return config


cfg_whatsapp_admin = config.get("admin_whatsapp", {})

cfg_menus = config.get("menús", {})
cfg_home = cfg_menus.get("inicio", {})
cfg_menu_paciente = cfg_menus.get("paciente", {})
cfg_menu_colaborador = cfg_menus.get("colaborador", {})

cfg_citas = config.get("citas", {})
cfg_citas_carnet = parse_campos(cfg_citas.get("carnet", {}))
cfg_citas_colaborador = parse_campos(cfg_citas.get("colaborador", {}))

cfg_espacios = parse_campos(config.get("espacios", {}))
