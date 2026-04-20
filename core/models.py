from django.db import models
from django.conf import settings

class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True)
    endereco = models.TextField(blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Servico(models.Model):
    PENDENTE = 'pendente'
    PAGO = 'pago'
    CANCELADO = 'cancelado'

    STATUS_CHOICES = [
        (PENDENTE, 'Pendente'),
        (PAGO, 'Pago'),
        (CANCELADO, 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='servicos')
    funcionario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='servicos',
    )
    data = models.DateField()
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    status_pagamento = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDENTE)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'
        ordering = ['-data']

    def __str__(self):
        return f'{self.cliente} — {self.data} — R$ {self.valor}'

