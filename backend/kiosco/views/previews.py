from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseRedirect

from ..utils import config, format, generate


def pdf(request: HttpRequest, tipo: str, id: str) -> HttpResponse:
    abrir = request.GET.get("abrir") == "1"

    if tipo == "citas_colaborador":
        persona = "colaborador"
        objetos = "citas"
        identificador = "nombre de usuario"
        data = config.cfg_citas_colaborador
    elif tipo == "citas_paciente":
        persona = "paciente"
        objetos = "citas"
        identificador = "carnet"
        data = config.cfg_citas_paciente
    elif tipo == "espacios":
        persona = None
        objetos = "espacios"
        identificador = None
        data = config.cfg_espacios
    else:
        return JsonResponse({"error": "Tipo inválido"}, status=400)

    filename = generate.pdf(
        id=id,
        format_func=format.campos,
        data=data,
        previous_context=request.session.get("context_data", {}),
        identificador=identificador,
        persona=persona,
        objetos=objetos,
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
