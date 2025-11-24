from datetime import date
from typing import Callable, Dict, Optional, Type, Union

from django.http import HttpRequest, JsonResponse

from classes.contexts import ContextList
from classes.models import BaseModel
from classes.selections import SelectionList
from ..models import Consulta
from ..utils import parse_queries


def api_query_view(
    request: HttpRequest,
    context_list: ContextList,
    selection_list: SelectionList,
    data_query: Optional[Callable] = None,
    *,
    url_params: Optional[Dict[str, Union[str, date]]] = None,
    model: Optional[Type[BaseModel]] = Consulta,
) -> JsonResponse:
    if not request.method == "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    payload = parse_queries(
        request=request,
        form_data=url_params,
        context_list=context_list,
        selection_list=selection_list,
        data_query=data_query,
        model=model,
        save_context=False,
    )
    return JsonResponse(payload, safe=False)
