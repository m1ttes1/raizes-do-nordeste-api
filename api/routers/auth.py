"""
Router de autenticação — implementa o fluxo OAuth2 com Password Flow (RNF02).

Neste padrão, o cliente envia e-mail e senha uma única vez para /login
e recebe um JWT que deve ser incluído no cabeçalho Authorization das
requisições seguintes. O servidor não mantém estado de sessão.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from application.auth_utils import criar_token_acesso
from application.schemas.auth_schemas import LoginInput, TokenResponse
from application.services.usuario_service import autenticar_usuario
from infrastructure.database import get_db

router = APIRouter(tags=["autenticação"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário e obter token de acesso",
)
def login(dados: LoginInput, db: Session = Depends(get_db)):
    """
    RF01/RNF02 — autentica o usuário e devolve um JWT Bearer token.

    O token carrega o e-mail ('sub') e o perfil do usuário no payload,
    permitindo que rotas protegidas identifiquem quem está fazendo
    a requisição sem consultar o banco a cada chamada.
    """
    try:
        usuario = autenticar_usuario(db, dados.email, dados.senha)
    except ValueError as e:
        # 401 sem detalhar se o erro é no e-mail ou na senha (anti-enumeração)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = criar_token_acesso({"sub": usuario.email, "perfil": usuario.perfil})
    return TokenResponse(access_token=token)
