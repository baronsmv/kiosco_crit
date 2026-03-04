from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from classes.contexts import ViewerContext
from utils.logger import get_logger

logger = get_logger(__name__)


def viewer_view(
    request: HttpRequest, template_name: str, context: ViewerContext
) -> HttpResponse:
    show_home = context.home.show
    home_label = context.home.label
    home_url = reverse_lazy(context.home.url_name)

    return render(
        request,
        template_name,
        {
            "title": context.title,
            "header": context.header,
            "show_home": show_home,
            "home_label": home_label,
            "home_url": home_url,
        },
    )
