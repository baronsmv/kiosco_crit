from datetime import date
from typing import Callable, Dict, Optional, Type, Union

from django.http import HttpRequest, JsonResponse

from classes.models import BaseModel
from ..models import Consulta
from ..utils import parse_queries, initial_context


def api_query_view(
    request: HttpRequest,
    config_data: Dict,
    exist_query: Optional[Callable] = None,
    data_query: Optional[Callable] = None,
    nombre_id: Optional[str] = None,
    nombre_sujeto: Optional[str] = None,
    nombre_objetos: Optional[str] = None,
    *,
    url_params: Optional[Dict[str, Union[str, date]]] = None,
    model: Optional[Type[BaseModel]] = Consulta,
) -> JsonResponse:
    if not request.method == "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    context = initial_context(config_data)
    parse_queries(
        request=request,
        form_data=url_params,
        config_data=config_data,
        context=context,
        exist_query=exist_query,
        data_query=data_query,
        nombre_id=nombre_id,
        nombre_sujeto=nombre_sujeto,
        nombre_objetos=nombre_objetos,
        model=model,
        save_context=False,
    )

    payload = {
        value: context.get(value) for value in ("sujeto", "tabla", "tabla_columnas")
    }
    return JsonResponse(payload, safe=False)
