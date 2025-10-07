from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from .. import models


class CitasCarnetConsultaTests(TestCase):
    def setUp(self):
        self.fecha = date.today()
        self.identificador = "12345678"
        self.estado = "exitoso"

    def test_model_creation(self):
        obj = models.consultas.CitasPaciente.objects.create(
            identificador=self.identificador,
            fecha_especificada=self.fecha,
            estado=self.estado,
        )
        self.assertEqual(obj.identificador, self.identificador)
        self.assertEqual(obj.fecha_especificada, self.fecha)
        self.assertEqual(obj.estado, self.estado)
        self.assertIsNotNone(obj.fecha_consulta)
        self.assertTrue(hasattr(obj, "carnet"))
        self.assertEqual(obj.carnet, self.identificador)

    def test_str_representation(self):
        obj = models.consultas.CitasPaciente.objects.create(
            identificador=self.identificador,
            fecha_especificada=self.fecha,
            estado=self.estado,
        )
        expected_str = f"{self.identificador} ({self.estado})"
        self.assertEqual(str(obj), expected_str)

    def test_estado_choices(self):
        # Probar que no permite un estado inválido
        obj = models.consultas.CitasPaciente(
            identificador=self.identificador,
            fecha_especificada=self.fecha,
            estado="invalido_123",
        )
        with self.assertRaises(ValidationError):
            obj.full_clean()

    def test_ip_cliente_optional(self):
        # No deberíamos necesitar pasar ip_cliente porque es nullable
        obj = models.consultas.CitasPaciente.objects.create(
            identificador=self.identificador,
            fecha_especificada=self.fecha,
            estado=self.estado,
        )
        self.assertIsNone(obj.ip_cliente)
