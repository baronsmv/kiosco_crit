from classes.contexts import ViewerContext, HomeSubContext
from menus import contexts

tabla_espacios_disponibles = ViewerContext(
    title="Espacios Disponibles",
    header="Espacios Disponibles",
    home=HomeSubContext(contexts.paciente.url_name),
)
