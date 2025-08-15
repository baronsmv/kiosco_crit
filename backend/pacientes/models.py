from django.db import models


class EnvioWhatsApp(models.Model):
    carnet = models.CharField(max_length=20)
    numero_destino = models.CharField(max_length=20)
    mensaje = models.TextField()
    archivo_pdf = models.CharField(max_length=255)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, choices=[("enviado", "Enviado"), ("fallido", "Fallido")]
    )
    detalle_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.carnet} → {self.numero_destino} ({self.estado})"
