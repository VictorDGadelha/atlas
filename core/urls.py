from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('peso/', views.peso, name='peso'),
    path('peso/<int:pk>/excluir/', views.peso_excluir, name='peso_excluir'),
]