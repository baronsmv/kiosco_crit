from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def agenda_espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return render(request, "viewers/agenda_espacios.html")
