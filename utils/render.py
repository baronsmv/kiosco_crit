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
    if filename == "status.html" and (
        "mensaje_ajax" not in context or "tipo_ajax" not in context
    ):
        logger.warning(f"El contexto de AJAX no tiene mensaje o tipo.")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        template = f"queries/partials/{filename}"
        logger.debug(f"Renderizando plantilla parcial: {template}")
        html = render_to_string(template, context, request=request)
        return HttpResponse(html)

    logger.warning("Petición no AJAX recibida (probablemente no configurada).")
    return None
