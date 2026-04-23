from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
]
    path('login/', views.login, name='login'),
]
