"""
Entidades do domínio — camada de regras de negócio pura.

Esses modelos Pydantic não sabem nada sobre banco de dados nem sobre HTTP;
só representam os conceitos do negócio e validam seus dados.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import CanalPedido, PerfilUsuario, StatusPedido


class Usuario(BaseModel):
    """Usuário do sistema com seu perfil de acesso (RF01)."""

    id: Optional[int] = None
    nome: str
    email: str
    perfil: PerfilUsuario


class Produto(BaseModel):
    """Produto do cardápio com controle de estoque por unidade (RF05)."""

    id: Optional[int] = None
    nome: str
    descricao: Optional[str] = None
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0)


class ItemPedido(BaseModel):
    id: Optional[int] = None
    produto_id: int
    quantidade: int = Field(gt=0)
    preco_unitario: float = Field(gt=0)


class Pedido(BaseModel):
    """
    Pedido central do sistema (RF03).

    canal_pedido é obrigatório por RF02: saber por onde o pedido chegou
    impacta a experiência do cliente e os relatórios gerenciais.
    """

    id: Optional[int] = None
    cliente_id: int
    canal_pedido: CanalPedido
    status: StatusPedido = StatusPedido.RECEBIDO
    itens: list[ItemPedido] = []
    criado_em: Optional[datetime] = None


class Pagamento(BaseModel):
    """RF04 — registra o resultado do pagamento simulado junto ao serviço externo."""

    id: Optional[int] = None
    pedido_id: int
    valor: float = Field(gt=0)
    aprovado: Optional[bool] = None


class Fidelizacao(BaseModel):
    """RF06 — pontuação acumulada do cliente para resgate de benefícios."""

    id: Optional[int] = None
    cliente_id: int
    pontos_acumulados: int = Field(ge=0, default=0)
