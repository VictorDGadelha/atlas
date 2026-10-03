from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('peso/', views.peso, name='peso'),
    path('peso/<int:pk>/excluir/', views.peso_excluir, name='peso_excluir'),
    path('alimentacao/', views.alimentacao, name='alimentacao'),
    path('alimentacao/<int:pk>/editar/', views.refeicao_editar, name='refeicao_editar'),
    path('alimentacao/<int:pk>/excluir/', views.refeicao_excluir, name='refeicao_excluir'),
    path('checklist/', views.checklist, name='checklist'),
    path('checklist/atividades/nova/', views.atividade_criar, name='atividade_criar'),
    path('checklist/atividades/<int:pk>/arquivar/', views.atividade_arquivar, name='atividade_arquivar'),
    path('checklist/marcar/<int:pk>/', views.checklist_marcar, name='checklist_marcar'),
    
]