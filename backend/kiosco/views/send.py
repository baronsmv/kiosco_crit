from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..utils import send
from ..utils.logger import get_logger

logger = get_logger(__name__)


def email_pdf(request: HttpRequest) -> HttpResponse | JsonResponse:
    return send.pdf_email(request)


@csrf_exempt
def whatsapp_pdf(request: HttpRequest) -> HttpResponse | JsonResponse:
    return send.pdf_whatsapp(request)
