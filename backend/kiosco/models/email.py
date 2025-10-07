from . import base


class CitasPacienteEmail(base.EmailIdFecha):
    @property
    def carnet(self):
        return self.identificador


class CitasColaboradorEmail(base.EmailIdFecha):
    pass


class EspaciosVaciosEmail(base.EmailFecha):
    pass
