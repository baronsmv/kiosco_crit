from django.db import models


class BaseModel(models.Model):
    tipo = models.CharField(max_length=50, db_index=True)
    identificador = models.CharField(max_length=20, blank=True, null=True)
    fecha_especificada = models.DateField(blank=True, null=True, db_index=True)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        abstract = True
