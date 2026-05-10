"""Enumerações do domínio da Raízes do Nordeste."""
from enum import Enum


class CanalPedido(str, Enum):
    """
    RF02 — canal pelo qual o pedido chegou ao sistema.

    Herdar de str faz o valor serializar diretamente como texto no JSON,
    sem precisar de conversões manuais entre a camada de API e o domínio.
    """

    APP = "APP"
    TOTEM = "TOTEM"
    BALCAO = "BALCAO"
    PICKUP = "PICKUP"
    WEB = "WEB"


class StatusPedido(str, Enum):
    """RF03 — ciclo de vida de um pedido, do recebimento à entrega."""

    RECEBIDO = "RECEBIDO"
    PREPARANDO = "PREPARANDO"
    PRONTO = "PRONTO"
    ENTREGUE = "ENTREGUE"


class PerfilUsuario(str, Enum):
    """RF01 — determina quais rotas e operações cada usuário pode acessar."""

    ADMIN = "ADMIN"
    ATENDENTE = "ATENDENTE"
    COZINHA = "COZINHA"
    CLIENTE = "CLIENTE"


class MetodoPagamento(str, Enum):
    """RF04 — forma de pagamento aceita pelo serviço simulado de cobrança."""

    CARTAO = "CARTAO"
    PIX = "PIX"
    DINHEIRO = "DINHEIRO"
