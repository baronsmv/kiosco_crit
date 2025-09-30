import hashlib
import os
from typing import Callable, Dict, Optional

from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from weasyprint import HTML

from . import map
from .logger import get_logger

logger = get_logger(__name__)


def pdf(
    format_func: Callable,
    data: Dict[str, Dict],
    previous_context: Dict,
    objetos: str,
    id: Optional[str] = None,
    persona: Optional[str] = None,
    identificador: Optional[str] = None,
    color: bool = False,
) -> str:
    pdf_data = data["pdf"]
    sql_data = data["sql"]

    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)

    if not previous_context:
        logger.error("previous_context está vacío. No se puede generar PDF.")
        raise ValueError("No hay datos de contexto en sesión.")

    logger.debug(f"Contexto recibido en generar_pdf: {previous_context.keys()}")

    fecha_especificada = previous_context.pop("fecha", None)

    try:
        formatted_context = format_func(
            **previous_context,
            campos=pdf_data.get("campos", ()),
            persona=persona,
            identificador=identificador,
        )
        previous_context.update(formatted_context)
    except Exception:
        logger.exception("Error al aplicar format_func en generar_pdf")
        raise

    # Render HTML
    try:
        html = render_to_string(
            "kiosco/pdf.html",
            {
                **pdf_data.get("context", {}),
                **previous_context,
                "tabla_columnas": map.columns(pdf_data, mapeo=sql_data),
            },
        )
    except Exception:
        logger.exception("Error al renderizar HTML")
        raise

    # Calcular hash del contenido HTML
    content_hash = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    filename = (
        "_".join(filter(None, (objetos, persona, id, fecha_especificada, content_hash)))
        + ".pdf"
    )
    output_path = os.path.join(output_dir, filename)
    logger.debug(f"Generando PDF en: {output_path}")

    # Buscar CSS
    css_path = finders.find(f"kiosco/css/pdf{'-color' if color else ''}.css")
    css_files = [css_path] if css_path else []

    try:
        HTML(string=html).write_pdf(output_path, stylesheets=css_files)
        logger.debug("PDF generado correctamente")
    except Exception:
        logger.exception("Error al generar el PDF")
        raise

    if not os.path.exists(output_path):
        logger.error(f"El archivo PDF no fue creado: {output_path}")
        raise FileNotFoundError("No se pudo generar el archivo PDF.")

    return filename
