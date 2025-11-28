from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Tuple


# Menús
@dataclass(frozen=True)
class MenuOptionSubContext:
    title: str
    description: str
    url_name: str


@dataclass(frozen=True)
class HomeSubContext:
    url_name: str = ""
    label: str = "Volver"
    show: bool = field(default=True)


@dataclass(frozen=True)
class CarouselSubContext:
    title: str = "Espacios Disponibles"
    show: bool = field(default=False)


@dataclass(frozen=True)
class MenuContext:
    title: str
    header: str
    url_name: str
    select_text: str = "Selecciona una opción para continuar:"
    options: Tuple[MenuOptionSubContext, ...] = ()
    carousel: CarouselSubContext = CarouselSubContext()
    home: HomeSubContext = HomeSubContext("home")


# Queries
@dataclass(frozen=True)
class IdSubContext:
    label: str
    placeholder: str
    max_length: int = 50
    pattern: str = r"^[a-zA-Z0-9. \-]+$"
    show: bool = field(default=True)
    required: bool = field(default=True)
    preserve: str = field(default=False)


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
    show: bool = field(default=True)
    required: bool = field(default=False)
    initial_date: Optional[date] = field(default_factory=lambda: date.today())
    preserve: bool = field(default=True)


@dataclass(frozen=True)
class SearchButtonSubContext:
    label: str = "Buscar"
    message: str = "Procesando..."


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
    button_label: str = "Descargar"
    show: bool = field(default=True)


@dataclass(frozen=True)
class SendResourceSubContext:
    label: str = "Enviar"
    url_name: str = ""
    show: bool = field(default=True)


@dataclass(frozen=True)
class SendPDFSubContext(SendResourceSubContext):
    label: str = "Enviar PDF"
    url_name: str = "send_email_pdf"


@dataclass(frozen=True)
class SendExcelSubContext(SendResourceSubContext):
    label: str = "Enviar Excel"
    url_name: str = "send_email_excel"


@dataclass(frozen=True)
class SendSubContext:
    title: str = "Envío"
    label: str = "A:"
    button_label: str = "Enviar"
    placeholder: str = "Ej. ejemplo"
    pattern_text: str = "No válido"
    pattern: Optional[str] = None
    send_label: str = "Enviar"
    show: bool = field(default=True)
    pdf: SendResourceSubContext = SendPDFSubContext()
    excel: SendResourceSubContext = SendExcelSubContext()


@dataclass(frozen=True)
class SendEmailSubContext(SendSubContext):
    title: str = "Envío por E-mail"
    label: str = "Correo electrónico:"
    button_label: str = "Enviar por e-mail"
    placeholder: str = "Ej: ejemplo@correo.com"
    pattern_text: str = "Debe ser un e-mail válido"


@dataclass(frozen=True)
class SendWhatsAppSubContext(SendSubContext):
    title: str = "Envío por WhatsApp"
    label: str = "Número telefónico:"
    button_label: str = "WhatsApp"
    placeholder: str = "Ej: 5512345678"
    pattern: Optional[str] = r"^\d{10}$"
    pattern_text: str = "Debe tener 10 dígitos numéricos"
    show: bool = field(default=False)


@dataclass(frozen=True)
class ModalContext:
    title: str
    data_title: str = ""
    table_title: str = ""
    pdf_preview: PreviewSubContext = PreviewSubContext("Vista previa e impresión")
    excel_preview: PreviewSubContext = PreviewSubContext("Descargar Excel")
    send_email: SendSubContext = SendEmailSubContext()
    send_whatsapp: SendSubContext = SendWhatsAppSubContext()


@dataclass(frozen=True)
class PDFContext:
    title: str
    header: str
    data_title: str = ""
    table_title: str = ""
    footer: str = "Fundación Teletón México A.C."


@dataclass(frozen=True)
class RedirectContext:
    url: str = "/"
    active: bool = field(default=True)
    after_minutes: int = 5
    countdown_seconds: int = 30


@dataclass(frozen=True)
class ContextList:
    initial: InitialWebContext
    modal: ModalContext
    pdf: PDFContext
    redirect: RedirectContext = RedirectContext(active=False)
    id_name: str = ""
    subject_name: str = ""
    objects_name: str = ""
