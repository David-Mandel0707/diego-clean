from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from .models import Servico

def lista_clientes(request):
    servicos = Servico.objects.select_related('cliente').all()
    return render(request, 'Home.html', {'servicos': servicos})

def home(request):
    return lista_clientes(request)
