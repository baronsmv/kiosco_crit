from datetime import date
from typing import Callable, Dict, Optional, Type, Union

from django.http import HttpRequest, JsonResponse

from classes.contexts import ContextList
from classes.models import BaseModel
from classes.selections import SelectionList
from ..models import Consulta
from ..utils import parse_query


def api_query_view(
    request: HttpRequest,
    query: Callable,
    selection_list: SelectionList,
    context_list: ContextList,
    url_params: Dict[str, Union[str, date]],
    *,
    model: Optional[Type[BaseModel]] = Consulta,
) -> JsonResponse:
    if not request.method == "GET":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    payload = parse_query(
        request=request,
        form_data=url_params,
        context_list=context_list,
        selection_list=selection_list,
        query=query,
        model=model,
        save_context=False,
    )
    return JsonResponse(payload, safe=False)
