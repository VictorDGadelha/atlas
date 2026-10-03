from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('peso/', views.peso, name='peso'),
    path('peso/<int:pk>/excluir/', views.peso_excluir, name='peso_excluir'),
    path('alimentacao/', views.alimentacao, name='alimentacao'),
    path('alimentacao/<int:pk>/editar/', views.refeicao_editar, name='refeicao_editar'),
    path('alimentacao/<int:pk>/excluir/', views.refeicao_excluir, name='refeicao_excluir'),
]