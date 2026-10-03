from django.contrib import admin
from .models import RegistroPeso, Refeicao, Atividade, AtividadeDia

admin.site.register(RegistroPeso)
admin.site.register(Refeicao)
admin.site.register(Atividade)
admin.site.register(AtividadeDia)