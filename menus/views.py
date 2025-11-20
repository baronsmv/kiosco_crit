from django.http import HttpRequest, HttpResponse

from menus.utils import menu_view
from utils.logger import get_logger
from . import contexts

logger = get_logger(__name__)


def home(request: HttpRequest) -> HttpResponse:
    return menu_view(request, contexts.inicio_context, contexts.inicio_options)


def paciente(request: HttpRequest) -> HttpResponse:
    return menu_view(request, contexts.paciente_context, contexts.paciente_options)


def colaborador(request: HttpRequest) -> HttpResponse:
    return menu_view(
        request, contexts.colaborador_context, contexts.colaborador_options
    )
