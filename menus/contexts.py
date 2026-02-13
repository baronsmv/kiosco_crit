from classes.contexts import (
    MenuContext,
    MenuOptionSubContext,
    HomeSubContext,
    CarouselSubContext,
)

# Opciones de submenús para otros menús
menu_paciente = MenuOptionSubContext(
    title="👤 Pacientes",
    description="Información relevante para pacientes.",
    url_name="menu_paciente",
)
menu_colaborador = MenuOptionSubContext(
    title="👤 Colaboradores",
    description="Información relevante para colaboradores.",
    url_name="menu_colaborador",
)

# Opciones de consultas para menús
citas_paciente = MenuOptionSubContext(
    title="🪪 Citas por Paciente",
    description="Busca citas con el carnet de un paciente.",
    url_name="citas_paciente",
)
prescripciones_paciente = MenuOptionSubContext(
    title="⚕ Prescripciones pendientes",
    description="Muestra las prescripciones pendientes de un paciente.",
    url_name="prescripciones_paciente",
)
datos_paciente = MenuOptionSubContext(
    title="📝 Datos del Paciente",
    description="Muestra los datos de un paciente.",
    url_name="datos_paciente",
)
citas_colaborador = MenuOptionSubContext(
    title="👤 Citas por Colaborador",
    description="Busca citas de un colaborador.",
    url_name="citas_colaborador",
)
espacios_disponibles = MenuOptionSubContext(
    title="📅 Espacios Disponibles",
    description="Muestra los espacios disponibles para agendar cita.",
    url_name="espacios_disponibles",
)

# Menús
inicio = MenuContext(
    title="Kiosco de Información",
    header="Kiosco de Información",
    url_name="home",
    options=(menu_paciente, menu_colaborador),
    home=HomeSubContext(show=False),
)
paciente = MenuContext(
    title="Kiosco de Información",
    header="Información para Pacientes",
    url_name=menu_paciente.url_name,
    options=(citas_paciente, datos_paciente),
    carousel=CarouselSubContext(show=True),
    home=HomeSubContext(inicio.url_name, show=False),
)
colaborador = MenuContext(
    title="Kiosco de Información",
    header="Información para Colaboradores",
    url_name=menu_colaborador.url_name,
    options=(citas_colaborador,),
    home=HomeSubContext(inicio.url_name, show=True),
)
