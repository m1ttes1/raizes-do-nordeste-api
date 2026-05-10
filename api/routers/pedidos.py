"""
Router de pedidos — endpoints de criação e consulta do fluxo de compras (RF02, RF03).

Multicanalidade (RF02): o campo canal_pedido é exigido em toda abertura de pedido,
identificando se a demanda veio do APP, TOTEM, BALCAO, PICKUP ou WEB.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from application.schemas.pedido_schemas import PagamentoCreate, PedidoCreate, PedidoResponse
from application.services.pedido_service import (
    buscar_pedido,
    criar_pedido,
    listar_pedidos,
    registrar_pagamento,
)
from infrastructure.database import get_db
from infrastructure.orm import UsuarioORM

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post("/", response_model=PedidoResponse, status_code=201)
def abrir_pedido(
    dados: PedidoCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioORM = Depends(get_current_user),
):
    """
    RF02 / RF03 — Abre um pedido identificando o canal de origem e baixando estoque.

    O cliente_id é extraído automaticamente do token JWT — o usuário autenticado
    é sempre o titular do pedido.
    """
    try:
        return criar_pedido(db, dados, cliente_id=usuario.id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/", response_model=List[PedidoResponse])
def listar(
    db: Session = Depends(get_db),
    usuario: UsuarioORM = Depends(get_current_user),
):
    """
    RF03 — Lista pedidos conforme o perfil do usuário autenticado.

    ADMIN / ATENDENTE / COZINHA visualizam todos os pedidos da rede.
    CLIENTE visualiza apenas o próprio histórico de compras.
    """
    return listar_pedidos(db, cliente_id=usuario.id, perfil=usuario.perfil)


@router.get("/{pedido_id}", response_model=PedidoResponse)
def detalhar(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: UsuarioORM = Depends(get_current_user),
):
    """RF03 — Retorna um pedido específico respeitando as regras de acesso por perfil."""
    try:
        return buscar_pedido(db, pedido_id, cliente_id=usuario.id, perfil=usuario.perfil)
    except ValueError as exc:
        codigo = 404 if "não encontrado" in str(exc) else 403
        raise HTTPException(status_code=codigo, detail=str(exc))


@router.post("/{pedido_id}/pagar", response_model=PedidoResponse)
def pagar(
    pedido_id: int,
    dados: PagamentoCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioORM = Depends(get_current_user),
):
    """
    RF04 — Registra o pagamento e aciona a produção na cozinha.

    Apenas o titular do pedido ou um ADMIN podem chamar esta rota.
    Ao confirmar o pagamento, o status transita de RECEBIDO para PREPARANDO.
    """
    try:
        return registrar_pagamento(
            db, pedido_id, dados, usuario_id=usuario.id, perfil=usuario.perfil
        )
    except ValueError as exc:
        codigos = {
            "não encontrado": 404,
            "Acesso negado": 403,
            "inferior ao total": 422,
            "já possui": 409,
            "status atual": 409,
        }
        codigo = next((v for k, v in codigos.items() if k in str(exc)), 422)
        raise HTTPException(status_code=codigo, detail=str(exc))
