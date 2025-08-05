from django.db import models


class Paciente(models.Model):
    carnet = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    diagnostico = models.TextField()
    grado = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()

    def __str__(self):
        return self.nombre

    def get_datos_dict(self):
        return {
            "Carnet": self.carnet,
            "Nombre": self.nombre,
            "Edad": self.edad,
            "Diagnóstico": self.diagnostico,
            "Grado": self.grado,
            "Fecha de ingreso": self.fecha_ingreso.strftime("%d/%m/%Y"),
        }


class EnvioWhatsApp(models.Model):
    paciente = models.ForeignKey("Paciente", on_delete=models.CASCADE)
    numero_destino = models.CharField(max_length=20)
    mensaje = models.TextField()
    archivo_pdf = models.CharField(max_length=255)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20, choices=[("enviado", "Enviado"), ("fallido", "Fallido")]
    )
    detalle_error = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.paciente.nombre} → {self.numero_destino} ({self.estado})"
