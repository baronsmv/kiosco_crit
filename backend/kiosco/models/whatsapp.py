from . import base


class CitasCarnetWA(base.WhatsappIdFecha):
    @property
    def carnet(self):
        return self.identificador


class CitasColaboradorWA(base.WhatsappIdFecha):
    pass


class EspaciosVaciosWA(base.WhatsappFecha):
    pass
