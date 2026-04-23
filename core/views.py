from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from decimal import Decimal
from .models import Servico, Cliente


def _login_required(view):
    return login_required(login_url='/login/')(view)


@_login_required
def home(request: HttpRequest):
    hoje = timezone.now().date()
    servicos_pendentes = Servico.objects.select_related('cliente').filter(status_pagamento=Servico.PENDENTE).order_by('-data')[:5]
    faturamento_mes = sum(
        s.valor for s in Servico.objects.filter(
            status_pagamento=Servico.PAGO,
            data__year=hoje.year,
            data__month=hoje.month,
        )
    ) or Decimal('0')
    pendentes_count = Servico.objects.filter(status_pagamento=Servico.PENDENTE).count()
    clientes_count = Cliente.objects.count()
    return render(request, 'Home.html', {
        'servicos_pendentes': servicos_pendentes,
        'faturamento_mes': faturamento_mes,
        'pendentes_count': pendentes_count,
        'clientes_count': clientes_count,
    })


@_login_required
def clientes(request: HttpRequest):
    lista = Cliente.objects.all()
    return render(request, 'Clientes.html', {'clientes': lista})


@_login_required
def novo_cliente(request: HttpRequest):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        endereco = request.POST.get('endereco', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()
        if nome:
            Cliente.objects.create(nome=nome, telefone=telefone, endereco=endereco, observacoes=observacoes)
            return redirect('clientes')
    return render(request, 'NovoCliente.html')


@_login_required
def cliente_detalhe(request: HttpRequest, pk: int):
    cliente = get_object_or_404(Cliente, pk=pk)
    servicos = cliente.servicos.all()
    return render(request, 'ClienteDetalhe.html', {'cliente': cliente, 'servicos': servicos})


@_login_required
def novo_servico(request: HttpRequest):
    clientes_lista = Cliente.objects.all()
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        data = request.POST.get('data')
        descricao = request.POST.get('descricao', '').strip()
        valor = request.POST.get('valor')
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        Servico.objects.create(
            cliente=cliente,
            funcionario=request.user,
            data=data,
            descricao=descricao,
            valor=valor,
        )
        return redirect('home')
    return render(request, 'NovoServico.html', {'clientes': clientes_lista})


@_login_required
def atualizar_status(request: HttpRequest, pk: int):
    if request.method == 'POST':
        servico = get_object_or_404(Servico, pk=pk)
        status = request.POST.get('status')
        if status in dict(Servico.STATUS_CHOICES):
            servico.status_pagamento = status
            servico.save()
    return redirect(request.POST.get('next', 'home'))
