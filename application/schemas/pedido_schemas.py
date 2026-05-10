"""Schemas de entrada e saída para o fluxo de pedidos e pagamentos (RF02, RF03, RF04)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field

from domain.enums import CanalPedido, MetodoPagamento, StatusPedido


class ItemPedidoCreate(BaseModel):
    """Item de linha enviado pelo cliente ao abrir um pedido."""

    produto_id: int
    quantidade: int = Field(gt=0, description="Quantidade deve ser maior que zero.")


class ItemPedidoResponse(BaseModel):
    """Representação de um item de pedido no retorno da API."""

    id: int
    produto_id: int
    quantidade: int
    preco_unitario: float

    model_config = {"from_attributes": True}


class PedidoCreate(BaseModel):
    """
    Dados necessários para abertura de um pedido.

    canal_pedido é obrigatório — identifica a origem da demanda e atende
    ao requisito de multicanalidade RF02 (APP, TOTEM, BALCAO, PICKUP, WEB).
    """

    # Multicanalidade: determina por qual canal o pedido chegou (RF02)
    canal_pedido: CanalPedido
    itens: List[ItemPedidoCreate] = Field(
        min_length=1,
        description="Pedido deve conter ao menos um item.",
    )


class PedidoResponse(BaseModel):
    """
    Dados retornados após criação ou consulta de um pedido.

    valor_total é derivado dinamicamente dos itens para garantir consistência
    com o preço registrado no momento da compra.
    """

    id: int
    cliente_id: int
    canal_pedido: CanalPedido
    status: StatusPedido
    itens: List[ItemPedidoResponse]
    criado_em: Optional[datetime] = None

    @computed_field
    @property
    def valor_total(self) -> float:
        """Soma de (quantidade × preco_unitario) de todos os itens do pedido."""
        return sum(item.quantidade * item.preco_unitario for item in self.itens)

    model_config = {"from_attributes": True}


class PagamentoCreate(BaseModel):
    """
    Dados enviados para registrar o pagamento de um pedido (RF04).

    O serviço de cobrança é simulado: a aprovação é automática quando
    o valor pago cobre o total do pedido.
    """

    metodo_pagamento: MetodoPagamento
    valor_pago: float = Field(gt=0, description="Valor em reais; deve ser maior que zero.")
