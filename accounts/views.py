from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def login(request):
    if request.user.is_authenticated:
        return HttpResponse("Site funcionando")
    if request.method=='POST':
        return HttpResponse("Site funcionando")
    return render(request, 'login.html')  
