from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from .models import cliente

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})

    return render(request, 'login.html')


def lista_clientes(request):
    clientes = cliente.objects.all()
    return render(request, 'clientes.html', {'clientes': clientes})
