from django.db import models

class Clima(models.Model):
    cidade = models.CharField(max_length=100, unique=True)
    temp_min = models.CharField(max_length=10, blank=True, null=True)
    temp_max = models.CharField(max_length=10, blank=True, null=True)
    sensacao = models.CharField(max_length=50, blank=True, null=True)
    chuva = models.CharField(max_length=50, blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cidade} - {self.atualizado_em}"



class Cidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    codigo_climatempo = models.IntegerField(unique=True)  # Código da cidade no Climatempo
    link_precipitacao = models.URLField()  # Link para o ClicTempo

    def __str__(self):
        return self.nome
