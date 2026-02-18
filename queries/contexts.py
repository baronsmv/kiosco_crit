from dataclasses import dataclass

from classes.contexts import (
    CarnetSubContext,
    NombreUsuarioSubContext,
    DateSubContext,
    InitialWebContext,
    ModalContext,
    PDFContext,
    ContextList,
    HomeSubContext,
    PreviewSubContext,
    SendEmailSubContext,
    SendExcelSubContext,
)
from menus import contexts


@dataclass(frozen=True)
class PacienteHomeSubContext(HomeSubContext):
    url_name: str = contexts.paciente.url_name


@dataclass(frozen=True)
class ColaboradorHomeSubContext(HomeSubContext):
    url_name: str = contexts.colaborador.url_name


citas_paciente = ContextList(
    initial=InitialWebContext(
        title="Búsqueda de citas",
        header="Búsqueda de citas",
        id=CarnetSubContext(),
        home=PacienteHomeSubContext(),
        date=DateSubContext(initial_date=None, preserve=False),
    ),
    modal=ModalContext(
        title="Ficha del Paciente",
        table_title="Citas",
        pdf_preview=PreviewSubContext(show=False),
        excel_preview=PreviewSubContext(show=False),
    ),
    pdf=PDFContext(
        title="Ficha del Paciente", header="Ficha del Paciente", table_title="Citas"
    ),
    id_name="carnet",
    subject_name="paciente",
    objects_name="citas",
)

datos_paciente = ContextList(
    initial=InitialWebContext(
        title="Datos del paciente",
        header="Datos del paciente",
        id=CarnetSubContext(),
        home=PacienteHomeSubContext(),
        date=DateSubContext(show=False),
    ),
    modal=ModalContext(
        title="Datos del paciente",
        pdf_preview=PreviewSubContext(show=False),
        excel_preview=PreviewSubContext(show=False),
        send_email=SendEmailSubContext(excel=SendExcelSubContext(show=False)),
    ),
    pdf=PDFContext(title="Datos del paciente", header="Datos del paciente"),
    id_name="carnet",
    subject_name="paciente",
    objects_name="datos",
)

citas_colaborador = ContextList(
    initial=InitialWebContext(
        title="Agenda del Colaborador",
        header="Agenda del Colaborador",
        id=NombreUsuarioSubContext(),
        date=DateSubContext(sublabel=None, required=True),
        home=ColaboradorHomeSubContext(),
    ),
    modal=ModalContext(
        title="Agenda del Colaborador",
        table_title="Citas",
    ),
    pdf=PDFContext(
        title="Agenda del Colaborador",
        header="Agenda del Colaborador",
        table_title="Citas",
    ),
    id_name="nombre de usuario",
    subject_name="colaborador",
    objects_name="citas",
)

espacios_disponibles = ContextList(
    initial=InitialWebContext(
        title="Espacios Disponibles",
        header="Espacios disponibles",
        id=CarnetSubContext(show=False),
        date=DateSubContext(sublabel=None, required=True),
        home=PacienteHomeSubContext(),
    ),
    modal=ModalContext(title="Espacios Disponibles"),
    pdf=PDFContext(title="Espacios Disponibles", header="Espacios Disponibles"),
    objects_name="espacios disponibles",
)

prescripciones = ContextList(
    initial=InitialWebContext(
        title="Prescripciones del Paciente",
        header="Prescripciones del Paciente",
        id=CarnetSubContext(),
        home=PacienteHomeSubContext(),
        date=DateSubContext(show=False),
    ),
    modal=ModalContext(
        title="Prescripciones del Paciente",
        pdf_preview=PreviewSubContext(show=False),
        excel_preview=PreviewSubContext(show=False),
        send_email=SendEmailSubContext(excel=SendExcelSubContext(show=False)),
    ),
    pdf=PDFContext(
        title="Prescripciones del Paciente", header="Prescripciones del Paciente"
    ),
    id_name="carnet",
    subject_name="paciente",
    objects_name="prescripciones",
)
