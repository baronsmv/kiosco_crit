from . import base


class CitasPaciente(base.ConsultaIdFecha):
    @property
    def carnet(self):
        return self.identificador


class CitasColaborador(base.ConsultaIdFecha):
    pass


class EspaciosVacios(base.ConsultaFecha):
    pass
