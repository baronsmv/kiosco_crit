from django.db import models

from classes.models import BaseModel


class EnvioWhatsapp(BaseModel):
    numero_destino = models.CharField(max_length=20)
    mensaje = models.TextField()
    archivo_pdf = models.CharField(max_length=255)
    estado = models.CharField(max_length=20)
    detalle_error = models.TextField(blank=True, null=True)

    fecha_envio = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        parts = []
        if self.identificador:
            parts.append(self.identificador)
        if self.fecha_especificada:
            parts.append(str(self.fecha_especificada))
        return f"{' '.join(parts)} → {self.numero_destino} ({self.estado})"

    class Meta:
        ordering = ["-fecha_envio"]


class EnvioEmail(BaseModel):
    correo_destino = models.EmailField()
    mensaje = models.TextField()
    archivo_pdf = models.CharField(max_length=255)
    estado = models.CharField(max_length=20)
    detalle_error = models.TextField(blank=True, null=True)

    fecha_envio = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.tipo} → {self.correo_destino} ({self.estado})"

    class Meta:
        ordering = ["-fecha_envio"]
