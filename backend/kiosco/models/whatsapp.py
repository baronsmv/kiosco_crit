from . import base


class CitasCarnet(base.WhatsappIdFecha):
    @property
    def carnet(self):
        return self.identificador


class CitasColaborador(base.WhatsappIdFecha):
    pass


class EspaciosVacios(base.WhatsappFecha):
    pass
