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
                    "formatear": "nombre",
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
                    "nombre": "Disponibles",
                    "sql": "kc.NO_DISPONIBLES",
                },
                "duracion_servicio": {
                    "nombre": "Duración",
                    "sql": "CONCAT(kc.NO_DURACION,' min')",
                },
                "inasistencias_paciente": {
                    "nombre": "Inasistencias",
                    "sql": "CP.NO_INASISTENCIAS",
                },
                "aniversario_paciente": {
                    "nombre": "Aniversario",
                    "sql": "CP.FE_ULTANIVERSARIO",
                },
                "deuda_total_paciente": {
                    "nombre": "Deuda total",
                    "sql": "CONVERT(DECIMAL(10,2), SUM(KSD.MN_TOTAL - KSD.MN_PAGADO))",
                },
            },
        },
    },
    "paciente": {
        "citas": {
            "web": {
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "clinica",
                    "estatus_cita",
                ],
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
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "estatus_cita",
                ],
                "context": {
                    "title": "Ficha del Paciente",
                    "header": "Ficha del Paciente",
                    "data_title": "",
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
                "campos": [
                    "no_carnet",
                    "nombre_paciente",
                    "clinica",
                    "inasistencias_paciente",
                    "aniversario_paciente",
                    "deuda_total_paciente",
                ],
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
            "sql": {
                "campos": [
                    "no_carnet",
                    "nombre_paciente",
                    "clinica",
                    "inasistencias_paciente",
                    "aniversario_paciente",
                    "deuda_total_paciente",
                ],
            },
        },
    },
    "colaborador": {
        "citas": {
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
                    "data_title": "",
                    "table_title": "Citas",
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
        "espacios disponibles": {
            "web": {
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "espacios_disponibles",
                    "duracion_servicio",
                ],
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
                "campos": [
                    "nombre_servicio",
                    "fecha_cita",
                    "nombre_colaborador",
                    "espacios_disponibles",
                    "duracion_servicio",
                ],
                "context": {
                    "title": "Espacios Disponibles",
                    "header": "Espacios Disponibles",
                    "data_title": "",
                    "table_title": "",
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
