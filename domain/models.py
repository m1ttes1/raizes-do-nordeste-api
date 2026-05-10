from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import CanalPedido, PerfilUsuario, StatusPedido


class Usuario(BaseModel):
    id: Optional[int] = None
    nome: str
    email: str
    perfil: PerfilUsuario


class Produto(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: Optional[str] = None
    preco: float = Field(gt=0)
    estoque: int = Field(ge=0)


class ItemPedido(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    preco_unitario: float = Field(gt=0)


class Pedido(BaseModel):
    id: Optional[int] = None
    cliente_id: int
    canal_pedido: CanalPedido  # RF02 — obrigatório, nunca omitir
    status: StatusPedido = StatusPedido.RECEBIDO
    itens: list[ItemPedido] = []
    criado_em: Optional[datetime] = None


class Pagamento(BaseModel):
    id: Optional[int] = None
    pedido_id: int
    valor: float = Field(gt=0)
    aprovado: Optional[bool] = None


class Fidelizacao(BaseModel):
    id: Optional[int] = None
    cliente_id: int
    pontos_acumulados: int = Field(ge=0, default=0)
