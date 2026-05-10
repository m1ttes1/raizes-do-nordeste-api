"""
Router de produtos — gerenciamento do cardápio da lanchonete (RF05).

O RBAC (controle de acesso baseado em perfil) protege as operações de escrita
exigindo que o usuário autenticado seja ADMIN ou COZINHA. Essa restrição garante
a integridade dos dados de inventário da lanchonete, impedindo que clientes ou
atendentes alterem preços e quantidades em estoque diretamente — conforme os
requisitos funcionais e não-funcionais do projeto (RF05, RNF02).

A listagem (GET /) é pública para que qualquer cliente consulte o cardápio
sem precisar de cadastro prévio.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from application.schemas.produto_schemas import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from application.services.produto_service import (
    atualizar_produto,
    criar_produto,
    deletar_produto,
    listar_produtos,
)
from domain.enums import PerfilUsuario
from infrastructure.database import get_db
from infrastructure.orm import UsuarioORM

router = APIRouter(prefix="/produtos", tags=["produtos"])

# Perfis autorizados a criar, editar e remover itens do cardápio
_PERFIS_GESTAO = {PerfilUsuario.ADMIN.value, PerfilUsuario.COZINHA.value}


def _exigir_gestor(usuario: UsuarioORM = Depends(get_current_user)) -> UsuarioORM:
    """
    Dependência de autorização: rejeita usuários sem permissão de gestão.

    Separa autenticação (quem é o usuário) de autorização (o que ele pode
    fazer), aplicando o princípio do menor privilégio (RNF02).
    """
    if usuario.perfil not in _PERFIS_GESTAO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a usuários com perfil ADMIN ou COZINHA.",
        )
    return usuario


@router.get(
    "/",
    response_model=List[ProdutoResponse],
    summary="Listar cardápio",
)
def listar(db: Session = Depends(get_db)):
    """RF05 — retorna todos os produtos disponíveis; rota pública para consulta do cardápio."""
    return listar_produtos(db)


@router.post(
    "/",
    response_model=ProdutoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar produto",
)
def cadastrar(
    dados: ProdutoCreate,
    db: Session = Depends(get_db),
    _: UsuarioORM = Depends(_exigir_gestor),
):
    """RF05 — cadastra novo produto no cardápio; exige perfil ADMIN ou COZINHA."""
    try:
        return criar_produto(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.put(
    "/{produto_id}",
    response_model=ProdutoResponse,
    summary="Atualizar produto",
)
def atualizar(
    produto_id: int,
    dados: ProdutoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioORM = Depends(_exigir_gestor),
):
    """RF05 — atualiza dados de um produto existente; exige perfil ADMIN ou COZINHA."""
    try:
        return atualizar_produto(db, produto_id, dados)
    except ValueError as e:
        msg = str(e)
        code = (
            status.HTTP_404_NOT_FOUND
            if "não encontrado" in msg
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=code, detail=msg)


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover produto",
)
def remover(
    produto_id: int,
    db: Session = Depends(get_db),
    _: UsuarioORM = Depends(_exigir_gestor),
):
    """RF05 — remove um produto do cardápio; exige perfil ADMIN ou COZINHA."""
    try:
        deletar_produto(db, produto_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
