from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse

from utils import generate
from utils.logger import get_logger

logger = get_logger(__name__)


def pdf(request: HttpRequest) -> HttpResponse | JsonResponse:
    previous_context = request.session.get("context_data", {})
    filename = generate.pdf(previous_context, color=False)
    file_url = f"/media/pdf/{filename}"

    if request.GET.get("abrir") == "1":
        return HttpResponseRedirect(file_url)

    iframe_html = f"""
    <div style="height: 60vh; margin-top: 2rem; padding: 1rem;">
        <iframe src="{file_url}" width="100%" height="100%" style="border: none; border-radius: 8px;"></iframe>
    </div>
    """
    return JsonResponse({"html": iframe_html, "filename": filename})


def excel(request: HttpRequest) -> HttpResponse:
    previous_context = request.session.get("context_data", {})
    filename = generate.excel(previous_context)
    file_url = f"/media/excel/{filename}"

    return HttpResponseRedirect(file_url)
