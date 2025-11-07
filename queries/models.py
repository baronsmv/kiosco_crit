from django.db import models

from classes.models import BaseModel


class Consulta(BaseModel):
    estado = models.CharField(max_length=20)

    fecha_consulta = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.tipo} → {self.identificador or ''} ({self.estado})"

    class Meta:
        ordering = ["-fecha_consulta"]
