from typing import Dict

import polars as pl
from django.conf import settings
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from weasyprint import HTML

from . import get, validate
from .logger import get_logger

logger = get_logger(__name__)


def pdf(context: Dict, color: bool = False, subdir: str = "pdf") -> str:
    validate.context(context)

    css_path = finders.find(f"previews/css/pdf{'-color' if color else ''}.css")
    css_files = (css_path,) if css_path else ()

    try:
        html = render_to_string(
            "previews/pdf.html",
            context,
        )
    except Exception:
        logger.exception("Error al renderizar HTML")
        raise

    filename = get.filename(context, ext="pdf", buffer=html.encode("utf-8"))
    output_path = get.output_path(dir=subdir, filename=filename)
    logger.debug(f"Generando PDF en: {output_path}")

    try:
        HTML(string=html).write_pdf(output_path, stylesheets=css_files)
    except Exception:
        logger.exception("Error al generar el PDF.")
        raise

    validate.output_file(output_path)
    logger.debug("PDF generado correctamente")
    return f"{settings.MEDIA_URL.strip("/")}/{subdir}/{filename}"


def excel(context: Dict, subdir: str = "excel") -> str:
    validate.context(context)

    df = pl.DataFrame(
        data=context["tabla_excel"],
        orient="row",
        schema=context["tabla_columnas_excel"],
    )
    logger.debug(f"DataFrame generado:\n{df.head()}")
    filename = get.filename(
        context, ext="xlsx", buffer=df.write_csv().encode()
    )
    output_path = get.output_path(dir=subdir, filename=filename)
    logger.debug(f"Generando Excel en: {output_path}")

    try:
        df.write_excel(output_path, worksheet="Hoja 1")
    except Exception:
        logger.exception("Error al generar el Excel.")
        raise

    validate.output_file(output_path)
    logger.debug("Excel generado correctamente")
    return f"{settings.MEDIA_URL.strip("/")}/{subdir}/{filename}"
