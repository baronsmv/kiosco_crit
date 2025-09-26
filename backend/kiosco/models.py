from django.db import models


class ConsultaBase(models.Model):
    fecha_consulta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=(
            ("exitoso", "Exitoso"),
            ("inexistente", "ID Inexistente"),
            ("sin_objetos", "Sin citas"),
            ("invalido", "ID Inválido"),
            ("error_conexion", "Error de conexión"),
        ),
    )
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        abstract = True


class ConsultaFechaBase(ConsultaBase):
    fecha_especificada = models.DateField()

    def __str__(self):
        return f"{self.fecha_especificada} ({self.estado})"


class ConsultaIdFechaBase(ConsultaBase):
    identificador = models.CharField(max_length=20)
    fecha_especificada = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(f"{self.identificador} ({self.estado})")


class WhatsappBase(models.Model):
    fecha_envio = models.DateTimeField(auto_now_add=True)
    numero_destino = models.CharField(max_length=20)
    mensaje = models.TextField()
    archivo_pdf = models.CharField(max_length=255)
    estado = models.CharField(
        max_length=20, choices=(("enviado", "Enviado"), ("fallido", "Fallido"))
    )
    detalle_error = models.TextField(blank=True, null=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        abstract = True


class WhatsappFechaBase(WhatsappBase):
    fecha_especificada = models.DateField()

    def __str__(self):
        return f"{self.fecha_especificada} → {self.numero_destino} ({self.estado})"


class WhatsappIdFechaBase(WhatsappBase):
    identificador = models.CharField(max_length=20)
    fecha_especificada = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.identificador} → {self.numero_destino} ({self.estado})"


class CitasCarnetConsulta(ConsultaIdFechaBase):
    @property
    def carnet(self):
        return self.identificador


class CitasCarnetWhatsapp(WhatsappIdFechaBase):
    @property
    def carnet(self):
        return self.identificador


class CitasColaboradorConsulta(ConsultaIdFechaBase):
    pass


class CitasColaboradorWhatsapp(WhatsappIdFechaBase):
    pass


class EspaciosVaciosConsulta(ConsultaFechaBase):
    pass


class EspaciosVaciosWhatsapp(WhatsappFechaBase):
    pass
