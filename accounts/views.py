from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def login(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello, World!")

    return render(request, "login.html")
