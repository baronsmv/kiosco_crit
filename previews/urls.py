from django.urls import path

from . import views

urlpatterns = [
    path(
        route="preview/excel/",
        view=views.excel,
        name="preview_excel",
    ),
    path(
        route="preview/pdf/",
        view=views.pdf,
        name="preview_pdf",
    ),
]
