from typing import Dict, Optional

from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

from .logger import get_logger

logger = get_logger(__name__)


def ajax_response(
    request: HttpRequest,
    context: Dict,
    *,
    filename: str = "status.html",
) -> Optional[HttpResponse]:
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = f"queries/partials/{filename}"
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
    logger.info("Petición no AJAX recibida (probablemente vista inicial).")
    return None
