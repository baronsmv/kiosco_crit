from typing import Dict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from ..utils import config


def _render_menu(request: HttpRequest, config: Dict[str, Dict]) -> HttpResponse:
    menu_options = tuple(
        (
            reverse_lazy(key),
            option.get("title", ""),
            option.get("description", ""),
        )
        for key, option in config.get("options", {}).items()
    )
    return render(
        request,
        "kiosco/menu.html",
        config.get("context", {})
        | {"home_url": reverse_lazy("home"), "menu_options": menu_options},
    )


def home(request: HttpRequest) -> HttpResponse:
    return _render_menu(request=request, config=config.cfg_home)


def paciente(request: HttpRequest) -> HttpResponse:
    return _render_menu(request=request, config=config.cfg_menu_paciente)


def colaborador(request: HttpRequest) -> HttpResponse:
    return _render_menu(request=request, config=config.cfg_menu_colaborador)
