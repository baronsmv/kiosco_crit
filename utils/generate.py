from typing import Dict

import polars as pl
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from weasyprint import HTML

from . import get, map, validate
from .logger import get_logger

logger = get_logger(__name__)


def filter_objects(context: Dict, data, sql_data) -> None:
    if not "objetos" in context:
        return

    context["tabla"] = get.filtered_objects(
        context["objetos"],
        campos=data.get("campos", {}),
        sql_campos=sql_data.get("campos", {}),
    )
    context["tabla_columnas"] = map.columns(data, sql_data=sql_data)


def pdf(context: Dict, color: bool = False) -> str:
    validate.context(context)
    pdf_data = context.get("pdf_data")
    sql_data = context.get("sql_data")
    filter_objects(context, pdf_data, sql_data)
    css_path = finders.find(f"previews/css/pdf{'-color' if color else ''}.css")
    css_files = (css_path,) if css_path else ()

    try:
        html = render_to_string(
            "previews/pdf.html",
            pdf_data.get("context", {}) | context,
        )
    except Exception:
        logger.exception("Error al renderizar HTML")
        raise

    filename = get.filename(context, ext="pdf", buffer=html.encode("utf-8"))
    output_path = get.output_path(dir="pdf", filename=filename)
    logger.debug(f"Generando PDF en: {output_path}")

    try:
        HTML(string=html).write_pdf(output_path, stylesheets=css_files)
    except Exception:
        logger.exception("Error al generar el PDF.")
        raise

    validate.output_file(output_path)
    logger.debug("PDF generado correctamente")
    return filename


def excel(context: Dict) -> str:
    validate.context(context)
    pdf_data = context.get("pdf_data")
    sql_data = context.get("sql_data")
    filter_objects(context, pdf_data, sql_data)

    df = pl.DataFrame(
        data=context["tabla"],
        orient="row",
        schema=map.columns(pdf_data, sql_data=sql_data),
    )
    logger.debug(f"DataFrame generado:\n{df.head()}")
    filename = get.filename(context, ext="xlsx", buffer=df.write_csv().encode())
    output_path = get.output_path(dir="excel", filename=filename)
    logger.debug(f"Generando Excel en: {output_path}")

    try:
        df.write_excel(output_path, worksheet="Hoja 1")
    except Exception:
        logger.exception("Error al generar el Excel.")
        raise

    validate.output_file(output_path)
    logger.debug("Excel generado correctamente")
    return filename
