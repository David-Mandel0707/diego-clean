from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Cliente

def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'Home.html', {'clientes': clientes})

def home(request):
    return HttpResponse("App funcionando")
