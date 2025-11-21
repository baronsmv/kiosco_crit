import sys
from unittest.mock import MagicMock

from django.test import TestCase

from classes.exceptions import AjaxException
from classes.selections import SelectionList, SelectClause

sys.modules["queries.models"] = MagicMock()

from queries.utils import get_objects


class GetObjectsLogicTests(TestCase):
    def setUp(self):
        self.selections = SelectionList(
            subject=(
                SelectClause(
                    name="Paciente",
                    sql_name="nombre_paciente",
                    sql_expression="...",
                ),
            ),
            web=(
                SelectClause(
                    name="Servicio",
                    sql_name="nombre_servicio",
                    sql_expression="...",
                ),
            ),
        )

    def test_subject_and_web(self):
        rows = [
            {
                "nombre_paciente": "Juan Pérez",
                "nombre_servicio": "Consulta",
                "fecha_cita": "21/11/2025 10:00",
            }
        ]
        result = get_objects(rows, self.selections, "id", "paciente", "citas")
        self.assertEqual(result["sujeto"]["Paciente"], "Juan Pérez")
        self.assertEqual(result["objetos"][0]["nombre_servicio"], "Consulta")

    def test_subject_only(self):
        selections = SelectionList(
            subject=(
                SelectClause(
                    name="Paciente", sql_name="nombre_paciente", sql_expression="..."
                ),
            ),
            web=(),
        )
        rows = [{"nombre_paciente": "Ana Gómez"}]
        result = get_objects(rows, selections, "id", "paciente", "citas")
        self.assertEqual(result["sujeto"]["Paciente"], "Ana Gómez")
        self.assertEqual(result["objetos"], [])

    def test_web_only(self):
        selections = SelectionList(
            subject=(),
            web=(
                SelectClause(
                    name="Servicio", sql_name="nombre_servicio", sql_expression="..."
                ),
            ),
        )
        rows = [{"nombre_servicio": "Consulta"}]
        result = get_objects(rows, selections, "id", "paciente", "citas")
        self.assertIsNone(result["sujeto"])
        self.assertEqual(result["objetos"][0]["nombre_servicio"], "Consulta")

    def test_no_rows_raises(self):
        rows = []
        with self.assertRaises(AjaxException):
            get_objects(rows, self.selections, "id", "paciente", "citas")
