"""
Router de usuários — traduz as requisições HTTP para chamadas ao service.

Nenhuma regra de negócio aqui: a validação dos dados fica no Pydantic
e a lógica fica no service. O router só mapeia erros para códigos HTTP.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies import get_current_user
from application.schemas.usuario_schemas import PontosResponse, UsuarioCreate, UsuarioResponse
from application.services.usuario_service import criar_usuario
from infrastructure.database import get_db
from infrastructure.orm import UsuarioORM

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuário",
)
def cadastrar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    """RF01 — cria um usuário com perfil definido (ADMIN, ATENDENTE, COZINHA ou CLIENTE)."""
    try:
        return criar_usuario(db, dados)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/me/pontos",
    response_model=PontosResponse,
    summary="Consultar saldo de pontos de fidelidade",
)
def consultar_pontos(usuario: UsuarioORM = Depends(get_current_user)):
    """
    RF06 — retorna o nome e o saldo atual de pontos de fidelidade do usuário autenticado.

    O cliente acumula 1 ponto por real pago em cada pedido confirmado.
    Aumentar o LTV (Lifetime Value) e a retenção é o objetivo desta
    funcionalidade, conforme boas práticas de Customer Experience:
    o extrato visível estimula novas compras e engajamento com a rede.
    """
    return PontosResponse.model_validate(usuario)
