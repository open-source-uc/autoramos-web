from django.db import models
from django.conf import settings

# Guarda los NRC's y los asocia a un usuario
class Planner(models.Model):
    """Modelo que guarda los NRC con un foreign key al usuario"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    nrc1 = models.CharField(max_length=5)
    nrc2 = models.CharField(max_length=5)
    nrc3 = models.CharField(max_length=5)
    nrc4 = models.CharField(max_length=5)
    nrc5 = models.CharField(max_length=5)
    nrc6 = models.CharField(max_length=5)
    estado_toma = models.IntegerField(null=True)
    hora_agendada = models.DateTimeField(blank=True)
    failed = models.CharField(max_length=3)
    
# Guarda los cookies del usuario
class Cookies(models.Model):
    user = models.CharField(max_length=255, unique=True)
    cookie_value = models.CharField(max_length=2000, blank=True, null=True)
    estado = models.BooleanField(default=True)
