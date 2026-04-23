from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import Cliente
from django.contrib.auth import authenticate, login as auth_login


def login(request):
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
            return render(request, 'Login.html', {'error': 'Usuário ou senha inválidos'})

    return render(request, 'login.html')
