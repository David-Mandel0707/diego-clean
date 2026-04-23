from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/novo/', views.novo_cliente, name='novo_cliente'),
    path('clientes/<int:pk>/', views.cliente_detalhe, name='cliente_detalhe'),
    path('clientes/<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('servicos/novo/', views.novo_servico, name='novo_servico'),
    path('servicos/<int:pk>/editar/', views.editar_servico, name='editar_servico'),
    path('historico/', views.historico, name='historico'),
    path('funcionarios/', views.funcionarios, name='funcionarios'),
    path('funcionarios/novo/', views.novo_funcionario, name='novo_funcionario'),
    path('funcionarios/<int:pk>/editar/', views.editar_funcionario, name='editar_funcionario'),
    path('funcionarios/<int:pk>/toggle/', views.toggle_funcionario, name='toggle_funcionario'),
    path('servicos/<int:pk>/status/', views.atualizar_status, name='atualizar_status'),
]
