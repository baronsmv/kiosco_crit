from dataclasses import asdict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from utils.logger import get_logger
from .contexts import MenuContext

logger = get_logger(__name__)


def menu_view(request: HttpRequest, context: MenuContext) -> HttpResponse:
    menu_options = tuple(
        (
            reverse_lazy(option.url_name),
            option.title,
            option.description,
        )
        for option in context.options
    )
    show_home = context.home.show
    home_label = context.home.label
    home_url = reverse_lazy(context.home.url_name)

    return render(
        request,
        "menus/menu.html",
        {
            "title": context.title,
            "header": context.header,
            "select_text": context.select_text,
            "menu_options": menu_options,
            "show_home": show_home,
            "home_label": home_label,
            "home_url": home_url,
            "carousel": asdict(context.carousel),
        },
    )
