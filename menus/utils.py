from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from utils.logger import get_logger
from .contexts import MenuContext, MenuOptions

logger = get_logger(__name__)


def menu_view(
    request: HttpRequest, context: MenuContext, options: MenuOptions
) -> HttpResponse:
    menu_options = tuple(
        (
            reverse_lazy(key),
            option.get("title", ""),
            option.get("description", ""),
        )
        for key, option in options.items()
    )
    return render(
        request,
        "menus/menu.html",
        context | {"home_url": reverse_lazy("home"), "menu_options": menu_options},
    )
