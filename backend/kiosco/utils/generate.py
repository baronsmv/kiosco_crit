import hashlib
import os
from typing import Dict

from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from weasyprint import HTML

from . import map
from .logger import get_logger

logger = get_logger(__name__)


def pdf(
    previous_context: Dict,
    salida_a_color: bool = False,
) -> str:
    if not previous_context:
        logger.error("previous_context está vacío. No se puede generar PDF.")
        raise ValueError("No hay datos de contexto en sesión.")

    pdf_data = previous_context.get("pdf_data")
    sql_data = previous_context.get("sql_data")

    output_dir = os.path.join(settings.MEDIA_ROOT, "pdfs")
    os.makedirs(output_dir, exist_ok=True)

    logger.debug(f"Contexto recibido en generar_pdf: {previous_context.keys()}")

    # Render HTML
    try:
        html = render_to_string(
            "kiosco/pdf.html",
            {
                **pdf_data.get("context", {}),
                **previous_context,
                "tabla_columnas": map.columns(pdf_data, sql_data=sql_data),
            },
        )
    except Exception:
        logger.exception("Error al renderizar HTML")
        raise

    content_hash = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    name_parts = tuple(
        previous_context.get(k)
        for k in (
            "nombre_objetos",
            "nombre_sujeto",
            "id",
            "fecha",
        )
    ) + (content_hash,)
    filename = "_".join(filter(None, name_parts)).replace(" ", "_") + ".pdf"
    output_path = os.path.join(output_dir, filename)
    logger.debug(f"Generando PDF en: {output_path}")

    css_path = finders.find(f"kiosco/css/pdf{'-color' if salida_a_color else ''}.css")
    css_files = (css_path,) if css_path else ()

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
