"""
Serviço de pedidos — orquestra criação com controle de estoque, consultas e pagamentos
(RF02, RF03, RF04).
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from application.schemas.pedido_schemas import PagamentoCreate, PedidoCreate, PedidoResponse
from domain.enums import PerfilUsuario, StatusPedido
from infrastructure.orm import ItemPedidoORM, PagamentoORM, PedidoORM, ProdutoORM

_PERFIS_IRRESTRITO = {
    PerfilUsuario.ADMIN.value,
    PerfilUsuario.ATENDENTE.value,
    PerfilUsuario.COZINHA.value,
}


def criar_pedido(db: Session, dados: PedidoCreate, cliente_id: int) -> PedidoResponse:
    """
    Abre um novo pedido verificando disponibilidade de estoque para cada item.

    Pré-valida todos os produtos antes de alterar qualquer registro, garantindo
    atomicidade: ou todos os itens são aceitos, ou nenhum estoque é decrementado.
    A baixa automática de estoque garante a consistência do inventário (RF03).
    """
    # Carrega e valida todos os produtos antes de gravar qualquer coisa
    produtos_map: dict[int, ProdutoORM] = {}
    for item in dados.itens:
        produto = db.query(ProdutoORM).filter(ProdutoORM.id == item.produto_id).first()
        if produto is None:
            raise ValueError(f"Produto com id {item.produto_id} não encontrado.")
        if produto.estoque < item.quantidade:
            raise ValueError(
                f"Estoque insuficiente para '{produto.nome}': "
                f"disponível {produto.estoque}, solicitado {item.quantidade}."
            )
        produtos_map[item.produto_id] = produto

    pedido_orm = PedidoORM(
        cliente_id=cliente_id,
        canal_pedido=dados.canal_pedido.value,
    )
    db.add(pedido_orm)
    # flush obtém o id gerado sem encerrar a transação, mantendo atomicidade
    db.flush()

    for item in dados.itens:
        produto = produtos_map[item.produto_id]
        # Baixa de estoque imediata: garante consistência do inventário (RF03)
        produto.estoque -= item.quantidade
        db.add(
            ItemPedidoORM(
                pedido_id=pedido_orm.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco_unitario=produto.preco,
            )
        )

    db.commit()
    db.refresh(pedido_orm)
    return PedidoResponse.model_validate(pedido_orm)


def listar_pedidos(db: Session, cliente_id: int, perfil: str) -> List[PedidoResponse]:
    """
    Retorna pedidos conforme o perfil do usuário autenticado.

    ADMIN, ATENDENTE e COZINHA enxergam todos os pedidos da rede.
    CLIENTE visualiza apenas o próprio histórico de compras.
    """
    if perfil in _PERFIS_IRRESTRITO:
        pedidos = db.query(PedidoORM).all()
    else:
        pedidos = db.query(PedidoORM).filter(PedidoORM.cliente_id == cliente_id).all()
    return [PedidoResponse.model_validate(p) for p in pedidos]


def buscar_pedido(
    db: Session, pedido_id: int, cliente_id: int, perfil: str
) -> PedidoResponse:
    """
    Retorna um pedido específico respeitando as regras de acesso por perfil.

    CLIENTE só pode consultar seus próprios pedidos; demais perfis têm acesso irrestrito.
    """
    pedido = db.query(PedidoORM).filter(PedidoORM.id == pedido_id).first()
    if pedido is None:
        raise ValueError("Pedido não encontrado.")
    if perfil not in _PERFIS_IRRESTRITO and pedido.cliente_id != cliente_id:
        raise ValueError("Acesso negado: este pedido pertence a outro cliente.")
    return PedidoResponse.model_validate(pedido)


def registrar_pagamento(
    db: Session,
    pedido_id: int,
    dados: PagamentoCreate,
    usuario_id: int,
    perfil: str,
) -> PedidoResponse:
    """
    Registra o pagamento de um pedido e aciona a produção na cozinha (RF03 / RF04).

    Apenas o titular do pedido ou um ADMIN podem efetuar o pagamento.
    O serviço de cobrança é simulado: aprovação automática quando o valor cobre o total.
    Ao confirmar o pagamento, o status transita de RECEBIDO para PREPARANDO —
    sinal para a cozinha iniciar a produção (RF03).
    """
    pedido = db.query(PedidoORM).filter(PedidoORM.id == pedido_id).first()
    if pedido is None:
        raise ValueError("Pedido não encontrado.")

    if perfil != PerfilUsuario.ADMIN.value and pedido.cliente_id != usuario_id:
        raise ValueError(
            "Acesso negado: apenas o titular do pedido ou um ADMIN podem efetuar o pagamento."
        )

    if pedido.status != StatusPedido.RECEBIDO.value:
        raise ValueError(
            f"Pedido não pode ser pago no status atual: {pedido.status}. "
            "Apenas pedidos com status RECEBIDO aceitam pagamento."
        )

    if pedido.pagamento is not None:
        raise ValueError("Este pedido já possui um pagamento registrado.")

    valor_total = sum(item.quantidade * item.preco_unitario for item in pedido.itens)
    if dados.valor_pago < valor_total:
        raise ValueError(
            f"Valor pago (R$ {dados.valor_pago:.2f}) é inferior ao total do pedido "
            f"(R$ {valor_total:.2f})."
        )

    db.add(
        PagamentoORM(
            pedido_id=pedido_id,
            valor=dados.valor_pago,
            metodo_pagamento=dados.metodo_pagamento.value,
            aprovado=True,
            processado_em=datetime.now(timezone.utc),
        )
    )

    # Pagamento confirmado aciona a produção: status RECEBIDO → PREPARANDO (RF03/RF04)
    pedido.status = StatusPedido.PREPARANDO.value

    # RF06 — acumula pontos de fidelidade: 1 ponto por real pago.
    # Estratégia de retenção e aumento de LTV (Lifetime Value) conforme
    # boas práticas de Customer Experience: o crédito ocorre no momento
    # em que a produção é confirmada, sinalizando comprometimento da rede.
    pedido.cliente.pontos_fidelidade += int(valor_total)

    db.commit()
    db.refresh(pedido)
    return PedidoResponse.model_validate(pedido)
