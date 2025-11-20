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
    "paciente": {
        "citas": {
            "web": {
                "context": {
                    "main": {
                        "title": "Búsqueda de citas",
                        "header": "Búsqueda de citas",
                        "id": {
                            "show": True,
                            "required": True,
                            "label": "Número de Carnet:",
                            "placeholder": "Ej: 123456",
                            "max_length": 20,
                            "pattern": r"^[a-zA-Z0-9. \-]+$",
                            "preserve": False,
                        },
                        "date": {
                            "show": True,
                            "required": False,
                            "label": "Fecha:",
                            "sublabel": "(Dejar vacío para mostrar todas)",
                            "initial": False,
                            "preserve": False,
                        },
                        "search_button": {
                            "label": "Buscar",
                            "message": "Procesando...",
                        },
                        "home": {
                            "show": True,
                            "label": "Volver",
                            "url": "menu_paciente",
                        },
                    },
                    "modal": {
                        "title": "Ficha del Paciente",
                        "data_title": "",
                        "table_title": "Citas",
                        "pdf_preview": {
                            "show": True,
                            "button_label": "Vista previa e impresión",
                        },
                        "excel_preview": {
                            "show": False,
                            "button_label": "Descargar Excel",
                        },
                        "send_email": {
                            "show": True,
                            "button_label": "Enviar por e-mail",
                            "title": "Envío por E-mail",
                            "email_label": "Correo electrónico:",
                            "placeholder": "Ej: ejemplo@correo.com",
                            "pattern_text": "Debe ser un e-mail válido",
                            "send_label": "Enviar",
                        },
                        "send_whatsapp": {
                            "show": False,
                            "button_label": "WhatsApp",
                            "title": "Envío por WhatsApp",
                            "number_label": "Número telefónico:",
                            "placeholder": "Ej: 5512345678",
                            "pattern": r"^\d{10}$",
                            "pattern_text": "Debe tener 10 dígitos numéricos",
                            "send_label": "Enviar",
                        },
                    },
                },
            },
            "pdf": {
                "context": {
                    "title": "Ficha del Paciente",
                    "header": "Ficha del Paciente",
                    "data_title": "",
                    "table_title": "Citas",
                    "footer": "Fundación Teletón México A.C.",
                },
            },
            "sql": {
                "filtros": {
                    "kpc.CL_ESTATUS_CITA": {
                        "con_fecha": ["A", "N"],
                        "sin_fecha": ["A"],
                    },
                },
            },
        },
        "datos": {
            "web": {
                "context": {
                    "main": {
                        "title": "Datos del paciente",
                        "header": "Datos del paciente",
                        "id": {
                            "show": True,
                            "required": True,
                            "label": "Número de Carnet:",
                            "placeholder": "Ej: 123456",
                            "max_length": 20,
                            "pattern": r"^[a-zA-Z0-9. \-]+$",
                            "preserve": False,
                        },
                        "date": {
                            "show": False,
                        },
                        "search_button": {
                            "label": "Buscar",
                            "message": "Procesando...",
                        },
                        "home": {
                            "show": True,
                            "label": "Volver",
                            "url": "menu_paciente",
                        },
                    },
                    "modal": {
                        "title": "Datos del Paciente",
                        "data_title": "",
                        "table_title": "",
                        "pdf_preview": {
                            "show": True,
                            "button_label": "Vista previa e impresión",
                        },
                        "excel_preview": {
                            "show": False,
                            "button_label": "Descargar Excel",
                        },
                        "send_email": {
                            "show": True,
                            "button_label": "Enviar por e-mail",
                            "title": "Envío por E-mail",
                            "email_label": "Correo electrónico:",
                            "placeholder": "Ej: ejemplo@correo.com",
                            "pattern_text": "Debe ser un e-mail válido",
                            "send_label": "Enviar",
                        },
                        "send_whatsapp": {
                            "show": False,
                            "button_label": "WhatsApp",
                            "title": "Envío por WhatsApp",
                            "number_label": "Número telefónico:",
                            "placeholder": "Ej: 5512345678",
                            "pattern": r"^\d{10}$",
                            "pattern_text": "Debe tener 10 dígitos numéricos",
                            "send_label": "Enviar",
                        },
                    },
                },
            },
            "pdf": {
                "campos": [
                    "no_carnet",
                    "nombre_paciente",
                    "clinica",
                    "inasistencias_paciente",
                    "aniversario_paciente",
                    "deuda_total_paciente",
                ],
                "context": {
                    "title": "Datos del Paciente",
                    "header": "Datos del Paciente",
                    "data_title": "",
                    "table_title": "",
                    "footer": "Fundación Teletón México A.C.",
                },
            },
        },
    },
    "colaborador": {
        "citas": {
            "web": {
                "context": {
                    "main": {
                        "title": "Agenda del Colaborador",
                        "header": "Agenda del Colaborador",
                        "id": {
                            "show": True,
                            "required": True,
                            "preserve": True,
                            "label": "Nombre de Usuario:",
                            "placeholder": "Ej: miguel.moedano",
                            "max_length": 20,
                            "pattern": r"^[a-zA-Z0-9. \-]+$",
                        },
                        "date": {
                            "show": True,
                            "required": True,
                            "initial": True,
                            "preserve": True,
                            "label": "Fecha:",
                            "sublabel": "",
                        },
                        "search_button": {
                            "label": "Buscar",
                            "message": "Procesando...",
                        },
                        "home": {
                            "show": True,
                            "label": "Volver",
                            "url": "menu_colaborador",
                        },
                    },
                    "modal": {
                        "title": "Agenda del Colaborador",
                        "data_title": "",
                        "table_title": "Citas",
                        "pdf_preview": {
                            "show": True,
                            "button_label": "Vista previa e impresión",
                        },
                        "excel_preview": {
                            "show": True,
                            "button_label": "Descargar Excel",
                        },
                        "send_email": {
                            "show": True,
                            "button_label": "Enviar por e-mail",
                            "title": "Envío por E-mail",
                            "email_label": "Correo electrónico:",
                            "placeholder": "Ej: ejemplo@correo.com",
                            "pattern_text": "Debe ser un e-mail válido",
                            "send_label": "Enviar",
                        },
                        "send_whatsapp": {
                            "show": False,
                            "button_label": "WhatsApp",
                            "title": "Envío por WhatsApp",
                            "number_label": "Número telefónico:",
                            "placeholder": "Ej: 5512345678",
                            "pattern": r"^\d{10}$",
                            "pattern_text": "Debe tener 10 dígitos numéricos",
                            "send_label": "Enviar",
                        },
                    },
                },
            },
            "pdf": {
                "context": {
                    "title": "Agenda del Colaborador",
                    "header": "Agenda del Colaborador",
                    "data_title": "",
                    "table_title": "Citas",
                    "footer": "Fundación Teletón México A.C.",
                },
            },
        },
        "espacios disponibles": {
            "web": {
                "context": {
                    "main": {
                        "title": "Espacios Disponibles",
                        "header": "Espacios Disponibles",
                        "id": {
                            "show": False,
                        },
                        "date": {
                            "show": True,
                            "required": True,
                            "label": "Fecha:",
                            "sublabel": "",
                            "initial": True,
                            "preserve": True,
                        },
                        "search_button": {
                            "label": "Buscar",
                            "message": "Procesando...",
                        },
                        "home": {
                            "show": True,
                            "label": "Volver",
                            "url": "menu_colaborador",
                        },
                    },
                    "modal": {
                        "title": "Espacios Disponibles",
                        "data_title": "",
                        "table_title": "",
                        "pdf_preview": {
                            "show": True,
                            "button_label": "Vista previa e impresión",
                        },
                        "excel_preview": {
                            "show": True,
                            "button_label": "Descargar Excel",
                        },
                        "send_email": {
                            "show": True,
                            "button_label": "Enviar por e-mail",
                            "title": "Envío por E-mail",
                            "email_label": "Correo electrónico:",
                            "placeholder": "Ej: ejemplo@correo.com",
                            "pattern_text": "Debe ser un e-mail válido",
                            "send_label": "Enviar",
                        },
                        "send_whatsapp": {
                            "show": False,
                            "button_label": "WhatsApp",
                            "title": "Envío por WhatsApp",
                            "number_label": "Número telefónico:",
                            "placeholder": "Ej: 5512345678",
                            "pattern": r"^\d{10}$",
                            "pattern_text": "Debe tener 10 dígitos numéricos",
                            "send_label": "Enviar",
                        },
                    },
                },
            },
            "pdf": {
                "context": {
                    "title": "Espacios Disponibles",
                    "header": "Espacios Disponibles",
                    "data_title": "",
                    "table_title": "",
                    "footer": "Fundación Teletón México A.C.",
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

cfg_paciente = config.get("paciente", {})
cfg_citas_paciente = parse_campos(cfg_paciente.get("citas", {}))
cfg_datos_paciente = parse_campos(cfg_paciente.get("datos", {}))

cfg_colaborador = config.get("colaborador", {})
cfg_citas_colaborador = parse_campos(cfg_colaborador.get("citas", {}))
cfg_espacios_disponibles = parse_campos(cfg_colaborador.get("espacios disponibles", {}))
