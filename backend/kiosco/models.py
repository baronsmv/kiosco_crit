from django.db import models


class ConsultaBase(models.Model):
    identificador = models.CharField(max_length=20)
    fecha_especificada = models.DateField(null=True, blank=True)
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.identificador)


class WhatsappBase(models.Model):
    identificador = models.CharField(max_length=20)
    numero_destino = models.CharField(max_length=20)
    mensaje = models.TextField()
    archivo_pdf = models.CharField(max_length=255)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, choices=[("enviado", "Enviado"), ("fallido", "Fallido")]
    )
    detalle_error = models.TextField(blank=True, null=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.identificador} → {self.numero_destino} ({self.estado})"


class CitasCarnetConsulta(ConsultaBase):
    @property
    def carnet(self):
        return self.identificador


class CitasCarnetWhatsapp(WhatsappBase):
    @property
    def carnet(self):
        return self.identificador


class CitasColaboradorConsulta(ConsultaBase):
    pass


class CitasColaboradorWhatsapp(WhatsappBase):
    pass
