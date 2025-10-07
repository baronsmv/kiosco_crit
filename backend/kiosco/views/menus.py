from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from ..utils import config, render
from ..utils.logger import get_logger

logger = get_logger(__name__)


def home(request: HttpRequest) -> HttpResponse:
    return render.menu(request=request, config=config.cfg_home)


def paciente(request: HttpRequest) -> HttpResponse:
    return render.menu(request=request, config=config.cfg_menu_paciente)


def colaborador(request: HttpRequest) -> HttpResponse:
    return render.menu(request=request, config=config.cfg_menu_colaborador)
