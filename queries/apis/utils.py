from typing import Callable, Dict, Optional, Type

from django.forms import Form
from django.http import HttpRequest, JsonResponse

from classes.models import BaseModel
from utils import get
from ..models import Consulta
from ..utils import parse_queries


def api_query_view(
    request: HttpRequest,
    config_data: Dict,
    form: Type[Form],
    data_query: Callable,
    nombre_objetos: str,
    *,
    model: Optional[Type[BaseModel]] = Consulta,
    nombre_id: Optional[str] = None,
    nombre_sujeto: Optional[str] = None,
    exist_query: Optional[Callable] = None,
) -> JsonResponse:
    context = get.initial_context(config_data)

    if request.method == "POST":
        parse_queries(
            request=request,
            config_data=config_data,
            context=context,
            form=form(request.POST),
            model=model,
            exist_query=exist_query,
            data_query=data_query,
            nombre_id=nombre_id,
            nombre_sujeto=nombre_sujeto,
            nombre_objetos=nombre_objetos,
        )

        payload = {
            "sujeto": context.get("sujeto"),
            "tabla": context.get("tabla"),
        }
        return JsonResponse(payload, safe=False)

    return JsonResponse({"error": "Método no permitido"}, status=405)
