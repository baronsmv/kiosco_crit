from . import base


class CitasPacienteWhatsapp(base.WhatsappIdFecha):
    @property
    def carnet(self):
        return self.identificador


class CitasColaboradorWhatsapp(base.WhatsappIdFecha):
    pass


class EspaciosVaciosWhatsapp(base.WhatsappFecha):
    pass
