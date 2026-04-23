from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Cliente
from django.contrib.auth import authenticate, login as auth_login


def login(request):
    if request.user.is_authenticated:
        return redirect('Home.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('Home.html')
        else:
            return render(request, 'login.html', {'error': 'Usuário ou senha inválidos'})

    return render(request, 'login.html')


def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes.html', {'clientes': clientes})

    if request.user.is_authenticated:
        return HttpResponse("Site funcionando")

    if request.method == 'POST':
        return HttpResponse("Site funcionando")

    return render(request, 'login.html')
