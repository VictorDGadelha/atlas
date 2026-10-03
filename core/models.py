from django.conf import settings
from django.db import models
from django.utils import timezone


class RegistroPeso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.DateField(default=timezone.localdate)
    peso = models.DecimalField(max_digits=5, decimal_places=2)  # em kg

    class Meta:
        ordering = ['-data']
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'data'], name='um_peso_por_dia')
        ]

    def __str__(self):
        return f'{self.data} - {self.peso} kg'


class Refeicao(models.Model):
    class Tipo(models.TextChoices):
        CAFE = 'cafe', 'Café da manhã'
        ALMOCO = 'almoco', 'Almoço'
        LANCHE = 'lanche', 'Lanche'
        JANTAR = 'jantar', 'Jantar'
        OUTRO = 'outro', 'Outro'

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.DateField(default=timezone.localdate)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    descricao = models.TextField()
    calorias = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-data', 'id']
        verbose_name = 'refeição'
        verbose_name_plural = 'refeições'

    def __str__(self):
        return f'{self.data} - {self.get_tipo_display()}'


class Atividade(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome = models.CharField(max_length=120)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class AtividadeDia(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE, related_name='registros')
    data = models.DateField(default=timezone.localdate)
    concluida = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['atividade', 'data'], name='uma_marcacao_por_dia')
        ]

    def __str__(self):
        return f'{self.atividade.nome} - {self.data} - {"ok" if self.concluida else "pendente"}'