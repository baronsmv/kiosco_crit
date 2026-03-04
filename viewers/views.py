from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from . import contexts
from .utils import viewer_view


def agenda_espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return render(request, "agendas/espacios_disponibles.html")


def tabla_espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return viewer_view(
        request,
        template_name="tablas/espacios_disponibles.html",
        context=contexts.tabla_espacios_disponibles,
    )
