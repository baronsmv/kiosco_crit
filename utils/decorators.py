from typing import Callable

from django.http import HttpRequest, HttpResponse

from classes.exceptions import AjaxException
from .logger import get_logger
from .render import ajax_response

logger = get_logger(__name__)


def ajax_handler(func: Callable) -> Callable:
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            return func(request, *args, **kwargs)
        except AjaxException as e:
            logger.info(
                f"Función {func.__name__} solicitando respuesta AJAX, "
                f"con contexto {e.get_context()} y template '{e.filename}'."
            )
            return ajax_response(request, context=e.get_context(), filename=e.filename)

    return wrapper
