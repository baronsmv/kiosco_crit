from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .. import models
from ..utils import send
from ..utils.logger import get_logger

logger = get_logger(__name__)


@csrf_exempt
def citas_paciente(request: HttpRequest) -> HttpResponse:
    return send.pdf(request, RegModel=models.CitasCarnetWhatsapp)


@csrf_exempt
def citas_colaborador(request: HttpRequest) -> HttpResponse:
    return send.pdf(request, RegModel=models.CitasColaboradorWhatsapp)


@csrf_exempt
def espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return send.pdf(request=request, RegModel=models.EspaciosVaciosWhatsapp)
