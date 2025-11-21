from django.http import HttpRequest, HttpResponse

from menus.utils import menu_view
from utils.logger import get_logger
from . import contexts

logger = get_logger(__name__)


def home(request: HttpRequest) -> HttpResponse:
    return menu_view(request, contexts.inicio)


def paciente(request: HttpRequest) -> HttpResponse:
    return menu_view(request, contexts.paciente)


def colaborador(request: HttpRequest) -> HttpResponse:
    return menu_view(request, contexts.colaborador)
