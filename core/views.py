from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
import pandas as pd
from .models import Servico, Cliente


def _login_required(view):
    return login_required(login_url='/login/')(view)


@_login_required
def home(request: HttpRequest):
    hoje = timezone.now().date()
    servicos_pendentes = Servico.objects.select_related('cliente').filter(status_pagamento=Servico.PENDENTE).order_by('-data')[:5]
    data_mes = list(Servico.objects.filter(
        status_pagamento=Servico.PAGO,
        data__year=hoje.year,
        data__month=hoje.month,
    ).values('valor'))
    df_mes = pd.DataFrame(data_mes)
    faturamento_mes = float(df_mes['valor'].sum()) if not df_mes.empty else 0.0
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
def historico(request: HttpRequest):
    qs = Servico.objects.select_related('cliente', 'funcionario').all()

    de = request.GET.get('de', '').strip()
    ate = request.GET.get('ate', '').strip()

    if de:
        qs = qs.filter(data__gte=de)
    if ate:
        qs = qs.filter(data__lte=ate)

    data_hist = list(qs.values('valor', 'status_pagamento'))
    df = pd.DataFrame(data_hist)
    total_faturado = float(df.loc[df['status_pagamento'] == Servico.PAGO, 'valor'].sum()) if not df.empty else 0.0
    total_servicos = len(df) if not df.empty else 0
    total_pendentes = int(df[df['status_pagamento'] == Servico.PENDENTE].shape[0]) if not df.empty else 0

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'Historico.html', {
        'page': page,
        'total_faturado': total_faturado,
        'total_servicos': total_servicos,
        'total_pendentes': total_pendentes,
        'filtro': {'de': de, 'ate': ate},
    })


@_login_required
def editar_cliente(request: HttpRequest, pk: int):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        if nome:
            cliente.nome = nome
            cliente.telefone = request.POST.get('telefone', '').strip()
            cliente.endereco = request.POST.get('endereco', '').strip()
            cliente.observacoes = request.POST.get('observacoes', '').strip()
            cliente.save()
            return redirect('cliente_detalhe', pk=pk)
    return render(request, 'EditarCliente.html', {'cliente': cliente})


@_login_required
def atualizar_status(request: HttpRequest, pk: int):
    if request.method == 'POST':
        servico = get_object_or_404(Servico, pk=pk)
        status = request.POST.get('status')
        if status in dict(Servico.STATUS_CHOICES):
            servico.status_pagamento = status
            servico.save()
    return redirect(request.POST.get('next', 'home'))
