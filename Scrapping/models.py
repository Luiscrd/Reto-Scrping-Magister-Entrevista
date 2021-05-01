from django.db import models
from django.templatetags.static import static

class Centros(models.Model):
    foto = models.ImageField(upload_to='%s/images'%(static))
    nombre = models.CharField(max_length=30)
    direccion = models.CharField(max_length=100)
    calle = models.CharField(max_length=30)
    numero = models.CharField(max_length=5)
    codigo = models.CharField(max_length=5)
    pobalcion = models.CharField(max_length=30)
    ciudad = models.CharField(max_length=30)
    tipo = models.CharField(max_length=30)
    latitud = models.FloatField(max_length=30, null=True, blank=True)
    longitud = models.FloatField(max_length=30, null=True, blank=True)