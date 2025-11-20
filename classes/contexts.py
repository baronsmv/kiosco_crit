from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class IdSubContext:
    label: str
    placeholder: str
    max_length: int = 50
    pattern: str = r"^[a-zA-Z0-9. \-]+$"
    show: bool = True
    required: bool = True
    preserve: str = False


@dataclass(frozen=True)
class CarnetSubContext(IdSubContext):
    label: str = "Número de Carnet:"
    placeholder: str = "Ej: 123456"


@dataclass(frozen=True)
class NombreUsuarioSubContext(IdSubContext):
    label: str = "Nombre de Usuario:"
    placeholder: str = "Ej: miguel.moedano"


@dataclass(frozen=True)
class DateSubContext:
    label: str = "Fecha:"
    sublabel: Optional[str] = "(Dejar vacío para mostrar todas)"
    show: bool = True
    required: bool = False
    initial_date: Optional[date] = date.today()
    preserve: bool = True


@dataclass(frozen=True)
class SearchButtonSubContext:
    label: str = "Buscar"
    message: str = "Procesando..."


@dataclass(frozen=True)
class HomeSubContext:
    url: str
    label: str = "Volver"
    show: bool = True


@dataclass(frozen=True)
class PacienteHomeSubContext(HomeSubContext):
    url: str = "menu_paciente"


@dataclass(frozen=True)
class ColaboradorHomeSubContext(HomeSubContext):
    url: str = "menu_colaborador"


@dataclass(frozen=True)
class InitialWebContext:
    title: str
    header: str
    id: IdSubContext
    home: HomeSubContext
    date: DateSubContext = DateSubContext()
    search_button: SearchButtonSubContext = SearchButtonSubContext()


@dataclass(frozen=True)
class PreviewSubContext:
    button_label: str
    show: bool = True


@dataclass(frozen=True)
class SendSubContext:
    title: str = "Envío"
    label: str = "A:"
    button_label: str = "Enviar"
    placeholder: str = "Ej. ejemplo"
    pattern_text: str = "No válido"
    pattern: Optional[str] = None
    send_label: str = "Enviar"
    show: bool = True


@dataclass(frozen=True)
class ModalContext:
    title: str
    data_title: str = ""
    table_title: str = ""
    pdf_preview: PreviewSubContext = PreviewSubContext("Vista previa e impresión")
    excel_preview: PreviewSubContext = PreviewSubContext("Descargar Excel")
    send_email: SendSubContext = SendSubContext(
        title="Envío por E-mail",
        label="Correo electrónico:",
        button_label="Enviar por e-mail",
        placeholder="Ej: ejemplo@correo.com",
        pattern_text="Debe ser un e-mail válido",
    )
    send_whatsapp: SendSubContext = SendSubContext(
        title="Envío por WhatsApp",
        label="Número telefónico:",
        button_label="WhatsApp",
        placeholder="Ej: 5512345678",
        pattern=r"^\d{10}$",
        pattern_text="Debe tener 10 dígitos numéricos",
        show=False,
    )


@dataclass(frozen=True)
class PDFContext:
    title: str
    header: str
    data_title: str = ""
    table_title: str = ""
    footer: str = "Fundación Teletón México A.C."


@dataclass(frozen=True)
class ContextList:
    initial: InitialWebContext
    modal: ModalContext
    pdf: PDFContext
