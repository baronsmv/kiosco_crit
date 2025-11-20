from typing import Dict, Union

MenuContext = Dict[str, Union[str, bool]]
MenuOptions = Dict[str, Dict[str, str]]

inicio_context: MenuContext = {
    "title": "Kiosco de Información",
    "header": "Kiosco de Información",
    "select_text": "Selecciona una opción para continuar:",
    "mostrar_inicio": False,
}
inicio_options: MenuOptions = {
    "menu_paciente": {
        "title": "👤 Pacientes",
        "description": "Información relevante para pacientes.",
    },
    "menu_colaborador": {
        "title": "👤 Colaboradores",
        "description": "Información relevante para colaboradores.",
    },
}

paciente_context: MenuContext = {
    "title": "Kiosco de Información",
    "header": "Información para Pacientes",
    "select_text": "Selecciona una opción para continuar:",
    "mostrar_inicio": True,
    "home_label": "Inicio",
}
paciente_options: MenuOptions = {
    "citas_paciente": {
        "title": "🪪 Citas por Paciente",
        "description": "Busca citas con el carnet de un paciente.",
    },
    "datos_paciente": {
        "title": "📝 Datos del Paciente",
        "description": "Muestra los datos de un paciente.",
    },
}

colaborador_context: MenuContext = {
    "title": "Kiosco de Información",
    "header": "Información para Colaboradores",
    "select_text": "Selecciona una opción para continuar:",
    "mostrar_inicio": True,
    "home_label": "Inicio",
}
colaborador_options: MenuOptions = {
    "citas_colaborador": {
        "title": "👤 Citas por Colaborador",
        "description": "Busca citas de un colaborador.",
    },
}
