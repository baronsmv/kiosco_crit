from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect

from ..utils import format, generate


def pdf(request: HttpRequest) -> HttpResponse:
    abrir = request.GET.get("abrir") == "1"
    previous_context = request.session.get("context_data", {})

    filename = generate.pdf(
        format_func=format.campos,
        previous_context=previous_context,
        salida_a_color=False,
    )
    file_url = f"/media/pdfs/{filename}"

    if abrir:
        return HttpResponseRedirect(file_url)

    iframe_html = f"""
    <div style="height: 60vh; margin-top: 2rem; padding: 1rem;">
        <iframe src="{file_url}" width="100%" height="100%" style="border: none; border-radius: 8px;"></iframe>
    </div>
    """
    return JsonResponse({"html": iframe_html, "filename": filename})
