from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from django.utils import timezone
import plotly.graph_objects as go
from .models import Servico, Cliente

def _login_required(view):
    return login_required(login_url='/login/')(view)


MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

_BAR_LAYOUT = dict(
    margin=dict(t=20, b=40, l=60, r=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(tickprefix='R$ ', gridcolor='#e5e7eb'),
    font=dict(family='inherit', size=12),
    height=280,
    autosize=True,
)

def _bar_html(fig, include_plotlyjs):
    return fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs, config={'displayModeBar': False, 'responsive': True})

def _vendas_por_mes(qs_pago_ano):
    totais = {m: 0.0 for m in range(1, 13)}
    for row in qs_pago_ano.values('data__month').annotate(total=Sum('valor')):
        totais[row['data__month']] = float(row['total'])
    return totais

def _vendas_por_ano(qs_pago):
    result = {}
    for row in qs_pago.values('data__year').annotate(total=Sum('valor')).order_by('data__year'):
        result[row['data__year']] = float(row['total'])
    return result

def _grafico_mensal(vendas, include_plotlyjs):
    valores = [vendas[m] for m in range(1, 13)]
    fig = go.Figure(go.Bar(
        x=MESES, y=valores, marker_color='#3498db',
        text=[f'R$ {v:,.2f}' for v in valores], textposition='outside',
    ))
    fig.update_layout(**_BAR_LAYOUT, xaxis=dict(gridcolor='rgba(0,0,0,0)'))
    return _bar_html(fig, include_plotlyjs)

def _grafico_anual(vendas, include_plotlyjs):
    anos = sorted(vendas.keys())
    fig = go.Figure(go.Bar(
        x=[str(a) for a in anos], y=[vendas[a] for a in anos], marker_color='#2ecc71',
        text=[f'R$ {vendas[a]:,.2f}' for a in anos], textposition='outside',
    ))
    fig.update_layout(**_BAR_LAYOUT, xaxis=dict(gridcolor='rgba(0,0,0,0)', type='category'))
    return _bar_html(fig, include_plotlyjs)


@_login_required
def home(request: HttpRequest):
    hoje = timezone.now().date()

    qs_pendentes = Servico.objects.select_related('cliente').filter(
        status_pagamento=Servico.PENDENTE, funcionario=request.user
    ).order_by('-data')

    faturamento_mes = float(
        Servico.objects.filter(
            status_pagamento=Servico.PAGO, data__year=hoje.year, data__month=hoje.month
        ).aggregate(total=Sum('valor'))['total'] or 0
    )
    pendentes_count = qs_pendentes.count()
    clientes_count = Cliente.objects.count()
    paginator = Paginator(qs_pendentes, 5)
    page_pendentes = paginator.get_page(request.GET.get('page'))

    grafico_pizza = grafico_mensal = grafico_anual = None
    grafico_mensal_proprio = grafico_anual_proprio = None

    if not request.user.is_superuser:
        qs_pago_proprio = Servico.objects.filter(status_pagamento=Servico.PAGO, funcionario=request.user)
        grafico_mensal_proprio = _grafico_mensal(
            _vendas_por_mes(qs_pago_proprio.filter(data__year=hoje.year)), 'cdn'
        )
        grafico_anual_proprio = _grafico_anual(_vendas_por_ano(qs_pago_proprio), False)

    if request.user.is_superuser:
        counts = Servico.objects.aggregate(
            pago=Count('pk', filter=Q(status_pagamento=Servico.PAGO)),
            pendente=Count('pk', filter=Q(status_pagamento=Servico.PENDENTE)),
            cancelado=Count('pk', filter=Q(status_pagamento=Servico.CANCELADO)),
        )
        fig_pizza = go.Figure(go.Pie(
            labels=['Realizados (Pago)', 'Pendentes', 'Cancelados'],
            values=[counts['pago'], counts['pendente'], counts['cancelado']],
            marker_colors=['#2ecc71', '#3498db', '#dc2626'],
            hole=0.35, textinfo='label+percent',
        ))
        fig_pizza.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, font=dict(family='inherit', size=13),
        )
        grafico_pizza = _bar_html(fig_pizza, 'cdn')

        qs_pago = Servico.objects.filter(status_pagamento=Servico.PAGO)
        grafico_mensal = _grafico_mensal(_vendas_por_mes(qs_pago.filter(data__year=hoje.year)), False)
        grafico_anual = _grafico_anual(_vendas_por_ano(qs_pago), False)

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

    agg = qs.aggregate(
        total_faturado=Sum('valor', filter=Q(status_pagamento=Servico.PAGO)),
        total_servicos=Count('pk'),
        total_pendentes=Count('pk', filter=Q(status_pagamento=Servico.PENDENTE)),
    )
    total_faturado = float(agg['total_faturado'] or 0)
    total_servicos = agg['total_servicos']
    total_pendentes = agg['total_pendentes']

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
