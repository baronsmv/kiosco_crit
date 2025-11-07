from django.http import HttpRequest, HttpResponse

from utils import render
from utils.logger import get_logger

logger = get_logger(__name__)


def pdf(request: HttpRequest) -> HttpResponse:
    return render.pdf(request=request)


def excel(request: HttpRequest) -> HttpResponse:
    return render.excel(request=request)
