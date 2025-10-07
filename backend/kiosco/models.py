from django.db import models


class Base(models.Model):
    tipo = models.CharField(max_length=50, db_index=True)
    identificador = models.CharField(max_length=20, blank=True, null=True)
    fecha_especificada = models.DateField(blank=True, null=True, db_index=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        abstract = True


class Consulta(Base):
    estado = models.CharField(max_length=20)

    fecha_consulta = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.tipo} → {self.identificador or ''} ({self.estado})"

    class Meta:
        ordering = ["-fecha_consulta"]


class EnvioWhatsapp(Base):
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


class EnvioEmail(Base):
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
