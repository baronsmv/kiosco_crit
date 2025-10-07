from django.http import HttpRequest, HttpResponse

from ..models import email
from ..utils.logger import get_logger
from ..utils.send import pdf_email

logger = get_logger(__name__)


def pdf_citas_paciente(request: HttpRequest) -> HttpResponse:
    return pdf_email(request, RegModel=email.CitasPacienteEmail)


def pdf_citas_colaborador(request: HttpRequest) -> HttpResponse:
    return pdf_email(request, RegModel=email.CitasColaboradorEmail)


def pdf_espacios_disponibles(request: HttpRequest) -> HttpResponse:
    return pdf_email(request=request, RegModel=email.EspaciosVaciosEmail)
