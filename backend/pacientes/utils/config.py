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
    "page_buscar_citas": {
        "context": {
            "title": "Búsqueda de citas",
            "header": "Búsqueda de citas",
            "form_label": "Número de Carnet:",
            "form_placeholder": "Ej: 123456",
            "button_label": "Buscar",
            "date_label": "Fecha:",
            "send_button_label": "📤 Enviar por WhatsApp",
            "tabla_titulo": "Citas",
        }
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
page_citas = config.get("page_buscar_citas", {})
