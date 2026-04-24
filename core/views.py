from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
import pandas as pd
import plotly.graph_objects as go
from .models import Servico, Cliente
from django.contrib.auth import get_user_model
from django.http import Http404

def _login_required(view):
    return login_required(login_url='/login/')(view)

@_login_required
def home(request: HttpRequest):
    hoje = timezone.now().date()
    
    qs_pendentes = Servico.objects.select_related('cliente').filter(status_pagamento=Servico.PENDENTE, funcionario=request.user).order_by('-data')
    data_mes = list(Servico.objects.filter(
        status_pagamento=Servico.PAGO,
        data__year=hoje.year,
        data__month=hoje.month,
    ).values('valor'))
    df_mes = pd.DataFrame(data_mes)
    faturamento_mes = float(df_mes['valor'].sum()) if not df_mes.empty else 0.0
    pendentes_count = qs_pendentes.count()
    clientes_count = Cliente.objects.count()
    paginator = Paginator(qs_pendentes, 5)
    page_pendentes = paginator.get_page(request.GET.get('page'))

    grafico_pizza = None
    grafico_mensal = None
    grafico_anual = None
    grafico_mensal_proprio = None
    grafico_anual_proprio = None

    MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

    if not request.user.is_superuser:
        vendas_mes_proprio = {m: 0.0 for m in range(1, 13)}
        for row in Servico.objects.filter(status_pagamento=Servico.PAGO, funcionario=request.user, data__year=hoje.year).values('data__month', 'valor'):
            vendas_mes_proprio[row['data__month']] += float(row['valor'])
        fig_mp = go.Figure(go.Bar(
            x=MESES,
            y=[vendas_mes_proprio[m] for m in range(1, 13)],
            marker_color='#2563eb',
            text=[f'R$ {v:,.2f}' for v in [vendas_mes_proprio[m] for m in range(1, 13)]],
            textposition='outside',
        ))
        fig_mp.update_layout(
            margin=dict(t=20, b=40, l=60, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(tickprefix='R$ ', gridcolor='#e5e7eb'),
            xaxis=dict(gridcolor='rgba(0,0,0,0)'),
            font=dict(family='inherit', size=12),
            height=280,
            autosize=True,
        )
        grafico_mensal_proprio = fig_mp.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False, 'responsive': True})

        vendas_ano_proprio: dict[int, float] = {}
        for row in Servico.objects.filter(status_pagamento=Servico.PAGO, funcionario=request.user).values('data__year', 'valor'):
            vendas_ano_proprio[row['data__year']] = vendas_ano_proprio.get(row['data__year'], 0.0) + float(row['valor'])
        anos_sorted_proprio = sorted(vendas_ano_proprio.keys())
        fig_ap = go.Figure(go.Bar(
            x=[str(a) for a in anos_sorted_proprio],
            y=[vendas_ano_proprio[a] for a in anos_sorted_proprio],
            marker_color='#16a34a',
            text=[f'R$ {vendas_ano_proprio[a]:,.2f}' for a in anos_sorted_proprio],
            textposition='outside',
        ))
        fig_ap.update_layout(
            margin=dict(t=20, b=40, l=60, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(tickprefix='R$ ', gridcolor='#e5e7eb'),
            xaxis=dict(gridcolor='rgba(0,0,0,0)', type='category'),
            font=dict(family='inherit', size=12),
            height=280,
            autosize=True,
        )
        grafico_anual_proprio = fig_ap.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})

    if request.user.is_superuser:
        counts = {s: 0 for s in [Servico.PAGO, Servico.PENDENTE, Servico.CANCELADO]}
        for row in Servico.objects.values('status_pagamento'):
            counts[row['status_pagamento']] = counts.get(row['status_pagamento'], 0) + 1
        fig_pizza = go.Figure(go.Pie(
            labels=['Realizados (Pago)', 'Pendentes', 'Cancelados'],
            values=[counts[Servico.PAGO], counts[Servico.PENDENTE], counts[Servico.CANCELADO]],
            marker_colors=['#16a34a', '#2563eb', '#dc2626'],
            hole=0.35,
            textinfo='label+percent',
        ))
        fig_pizza.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            font=dict(family='inherit', size=13),
        )
        grafico_pizza = fig_pizza.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': False, 'responsive': True})

        vendas_mes = {m: 0.0 for m in range(1, 13)}
        for row in Servico.objects.filter(status_pagamento=Servico.PAGO, data__year=hoje.year).values('data__month', 'valor'):
            vendas_mes[row['data__month']] += float(row['valor'])
        fig_mensal = go.Figure(go.Bar(
            x=MESES,
            y=[vendas_mes[m] for m in range(1, 13)],
            marker_color='#2563eb',
            text=[f'R$ {v:,.2f}' for v in [vendas_mes[m] for m in range(1, 13)]],
            textposition='outside',
        ))
        fig_mensal.update_layout(
            margin=dict(t=20, b=40, l=60, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(tickprefix='R$ ', gridcolor='#e5e7eb'),
            xaxis=dict(gridcolor='rgba(0,0,0,0)'),
            font=dict(family='inherit', size=12),
            height=280,
            autosize=True,
        )
        grafico_mensal = fig_mensal.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})

        vendas_ano: dict[int, float] = {}
        for row in Servico.objects.filter(status_pagamento=Servico.PAGO).values('data__year', 'valor'):
            vendas_ano[row['data__year']] = vendas_ano.get(row['data__year'], 0.0) + float(row['valor'])
        anos_sorted = sorted(vendas_ano.keys())
        fig_anual = go.Figure(go.Bar(
            x=[str(a) for a in anos_sorted],
            y=[vendas_ano[a] for a in anos_sorted],
            marker_color='#16a34a',
            text=[f'R$ {vendas_ano[a]:,.2f}' for a in anos_sorted],
            textposition='outside',
        ))
        fig_anual.update_layout(
            margin=dict(t=20, b=40, l=60, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(tickprefix='R$ ', gridcolor='#e5e7eb'),
            xaxis=dict(gridcolor='rgba(0,0,0,0)', type='category'),
            font=dict(family='inherit', size=12),
            height=280,
            autosize=True,
        )
        grafico_anual = fig_anual.to_html(full_html=False, include_plotlyjs=False, config={'displayModeBar': False, 'responsive': True})

    return render(request, 'Home.html', {
        'page_pendentes': page_pendentes,
        'faturamento_mes': faturamento_mes,
        'pendentes_count': pendentes_count,
        'clientes_count': clientes_count,
        'grafico_pizza': grafico_pizza,
        'grafico_mensal': grafico_mensal,
        'grafico_anual': grafico_anual,
        'grafico_mensal_proprio': grafico_mensal_proprio,
        'grafico_anual_proprio': grafico_anual_proprio,
        'hoje': hoje,
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
    status_filtro = request.GET.get('status', '').strip()
    vendedor_id = request.GET.get('vendedor', '').strip()

    if de:
        qs = qs.filter(data__gte=de)
    if ate:
        qs = qs.filter(data__lte=ate)
    if status_filtro in [Servico.PAGO, Servico.PENDENTE, Servico.CANCELADO]:
        qs = qs.filter(status_pagamento=status_filtro)
    if vendedor_id.isdigit():
        qs = qs.filter(funcionario_id=int(vendedor_id))

    User = get_user_model()
    vendedores = User.objects.filter(servicos__isnull=False).distinct().order_by('first_name', 'username')

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
        'filtro': {'de': de, 'ate': ate, 'status': status_filtro, 'vendedor': vendedor_id},
        'vendedores': vendedores,
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
def funcionarios(request: HttpRequest):
    if not request.user.is_superuser:
        return redirect('home')
    User = get_user_model()
    qs = User.objects.filter(is_superuser=False).order_by('first_name', 'username')
    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'Funcionarios.html', {'page': page})

def _superuser_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.is_superuser:
            raise Http404
        return view(request, *args, **kwargs)
    wrapper.__name__ = view.__name__
    return wrapper


@_superuser_required
def novo_funcionario(request: HttpRequest):
    User = get_user_model()
    erro = None
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip().lower()
        senha = request.POST.get('senha', '').strip()
        if not first_name or not username or not senha:
            erro = 'Nome, usuário e senha são obrigatórios.'
        elif User.objects.filter(username=username).exists():
            erro = 'Esse nome de usuário já está em uso.'
        else:
            User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=senha)
            return redirect('funcionarios')
    return render(request, 'NovoFuncionario.html', {'erro': erro})


@_superuser_required
def editar_funcionario(request: HttpRequest, pk: int):
    User = get_user_model()
    func = get_object_or_404(User, pk=pk, is_superuser=False)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        username = request.POST.get('username', '').strip().lower()
        if not first_name or not username:
            return render(request, 'EditarFuncionario.html', {'func': func, 'erro': 'Nome e usuário são obrigatórios.'})
        func.first_name = first_name
        func.last_name = request.POST.get('last_name', '').strip()
        func.username = username
        senha = request.POST.get('senha', '').strip()
        if senha:
            func.set_password(senha)
        func.save()
        return redirect('funcionarios')
    return render(request, 'EditarFuncionario.html', {'func': func})


@_superuser_required
def toggle_funcionario(request: HttpRequest, pk: int):
    User = get_user_model()
    if request.method == 'POST':
        func = get_object_or_404(User, pk=pk, is_superuser=False)
        func.is_active = not func.is_active
        func.save()
    return redirect('funcionarios')


@_login_required
def editar_servico(request: HttpRequest, pk: int):
    servico = get_object_or_404(Servico, pk=pk)
    if servico.funcionario != request.user and not request.user.is_superuser:
        return redirect('home')
    clientes_lista = Cliente.objects.all()
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        data = request.POST.get('data')
        descricao = request.POST.get('descricao', '').strip()
        valor = request.POST.get('valor')
        status = request.POST.get('status_pagamento')
        if cliente_id and data and valor:
            servico.cliente = get_object_or_404(Cliente, pk=cliente_id)
            servico.data = data
            servico.descricao = descricao
            servico.valor = valor
            if status in dict(Servico.STATUS_CHOICES):
                servico.status_pagamento = status
            servico.save()
            return redirect('cliente_detalhe', pk=servico.cliente.pk)
    return render(request, 'EditarServico.html', {'servico': servico, 'clientes': clientes_lista})


@_login_required
def atualizar_status(request: HttpRequest, pk: int):
    if request.method == 'POST':
        servico = get_object_or_404(Servico, pk=pk)
        if servico.funcionario == request.user or request.user.is_superuser:
            status = request.POST.get('status')
            if status in dict(Servico.STATUS_CHOICES):
                servico.status_pagamento = status
                servico.save()
    return redirect(request.POST.get('next', 'home'))
