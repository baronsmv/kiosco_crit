from datetime import date
from typing import Callable, Optional, Type

from django.db import OperationalError
from django.http import HttpRequest, HttpResponse

from classes import models
from classes.exceptions import AjaxException
from queries.models import Consulta
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


def query_handler(func: Callable) -> Callable:
    def wrapper(
        id: Optional[str] = None,
        fecha: Optional[date] = None,
        tipo: str = None,
        ip_cliente: Optional[str] = None,
        model: Optional[Type[models.BaseModel]] = Consulta,
        *args,
        **kwargs,
    ) -> HttpResponse:
        try:
            return func(
                id=id,
                fecha=fecha,
                tipo=tipo,
                ip_cliente=ip_cliente,
                model=model,
                *args,
                **kwargs,
            )
        except OperationalError as e:
            logger.error(f"Error de conexión a la base de datos: {e}")
            if model:
                model.objects.create(
                    tipo=tipo,
                    identificador=id,
                    fecha_especificada=fecha,
                    ip_cliente=ip_cliente,
                    estado="Error de conexión",
                )
            raise AjaxException("❌ No se pudo conectar con la base de datos.")
        except AjaxException as e:
            if model:
                model.objects.create(
                    tipo=tipo,
                    identificador=id,
                    fecha_especificada=fecha,
                    ip_cliente=ip_cliente,
                    estado=e.causa,
                )
            raise

    return wrapper
