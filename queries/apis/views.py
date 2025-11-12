from utils import config
from .utils import BaseConsultaAPIView
from .. import forms, queries


class CitasPaciente(BaseConsultaAPIView):
    config_data = config.cfg_citas_paciente
    form_class = forms.BuscarIdFechaForm
    exist_query = queries.exist.paciente
    data_query = queries.data.citas_paciente
    nombre_id = "carnet"
    nombre_sujeto = "paciente"
    nombre_objetos = "citas"


class DatosPaciente(BaseConsultaAPIView):
    config_data = config.cfg_datos_paciente
    form_class = forms.BuscarIdForm
    exist_query = queries.exist.paciente
    data_query = queries.data.datos_paciente
    nombre_id = "carnet"
    nombre_sujeto = "paciente"
    nombre_objetos = "datos"


class CitasColaborador(BaseConsultaAPIView):
    config_data = config.cfg_citas_colaborador
    form_class = forms.BuscarIdFechaForm
    exist_query = queries.exist.colaborador
    data_query = queries.data.citas_colaborador
    nombre_id = "nombre de usuario"
    nombre_sujeto = "colaborador"
    nombre_objetos = "citas"


class EspaciosDisponibles(BaseConsultaAPIView):
    config_data = config.cfg_espacios_disponibles
    form_class = forms.BuscarFechaForm
    data_query = queries.data.espacios_disponibles
    nombre_objetos = "espacios disponibles"
