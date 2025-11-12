from typing import Dict


class AjaxException(Exception):
    def __init__(
        self,
        mensaje: str = "Error al obtener datos. Favor de informar a TI.",
        *,
        tipo: str = "error",
        causa: str = "Error Desconocido",
        target: str = "id",
        status: int = 400,
        context: Dict = None,
        filename: str = "status.html",
    ):
        self.mensaje: str = mensaje
        self.tipo: str = tipo
        self.causa: str = causa
        self.target: str = target
        self.status: int = status
        self.context: Dict = context
        self.filename: str = filename
        super().__init__(mensaje)

    def get_context(self) -> Dict[str, str]:
        if isinstance(self.context, dict):
            return self.context
        return {"mensaje_ajax": self.mensaje, "tipo_ajax": self.tipo}
