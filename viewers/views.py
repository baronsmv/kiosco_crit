from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def agenda_espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return render(request, "agendas/espacios_disponibles.html")
