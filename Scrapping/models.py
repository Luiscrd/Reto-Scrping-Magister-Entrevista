from django.db import models
from django.templatetags.static import static

class Centros(models.Model):
    foto = models.CharField(max_length=150, null=True, blank=True)
    nombre = models.CharField(max_length=30, null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    calle = models.CharField(max_length=30, null=True, blank=True)
    numero = models.CharField(max_length=5, null=True, blank=True)
    codigo = models.CharField(max_length=5, null=True, blank=True)
    pobalcion = models.CharField(max_length=30, null=True, blank=True)
    ciudad = models.CharField(max_length=30, null=True, blank=True)
    tipo = models.CharField(max_length=30, null=True, blank=True)
    latitud = models.FloatField(max_length=30, null=True, blank=True)
    longitud = models.FloatField(max_length=30, null=True, blank=True)