from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
]
