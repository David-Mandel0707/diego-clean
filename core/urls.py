from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/novo/', views.novo_cliente, name='novo_cliente'),
    path('clientes/<int:pk>/', views.cliente_detalhe, name='cliente_detalhe'),
    path('servicos/novo/', views.novo_servico, name='novo_servico'),
    path('servicos/<int:pk>/status/', views.atualizar_status, name='atualizar_status'),
]
