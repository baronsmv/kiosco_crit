from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from utils import generate
from utils.logger import get_logger

logger = get_logger(__name__)


def pdf(request: HttpRequest) -> HttpResponse:
    previous_context = request.session.get("context_data", {})
    file_url = generate.pdf(previous_context, color=False, as_str=True)

    return HttpResponseRedirect(file_url)


def excel(request: HttpRequest) -> HttpResponse:
    previous_context = request.session.get("context_data", {})
    file_url = generate.excel(previous_context, as_str=True)

    return HttpResponseRedirect(file_url)
