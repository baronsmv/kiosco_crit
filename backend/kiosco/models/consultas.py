from . import base


class CitasCarnet(base.ConsultaIdFecha):
    @property
    def carnet(self):
        return self.identificador


class CitasColaborador(base.ConsultaIdFecha):
    pass


class EspaciosVacios(base.ConsultaFecha):
    pass
