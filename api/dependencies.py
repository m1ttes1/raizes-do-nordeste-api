"""
Dependências reutilizáveis da camada de API.

get_current_user é a principal proteção das rotas autenticadas:
extrai o Bearer token do cabeçalho, valida a assinatura JWT e
retorna o usuário correspondente. Qualquer rota que receba essa
dependency como parâmetro exige login obrigatório.

O esquema OAuth2PasswordBearer informa ao Swagger qual endpoint
usar para obter o token, habilitando o botão 'Authorize' na
documentação interativa — um requisito do RNF04.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from application.auth_utils import decodificar_token
from infrastructure.database import get_db
from infrastructure.orm import UsuarioORM

# tokenUrl aponta para o endpoint de login que emite os tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UsuarioORM:
    """
    Valida o JWT recebido e retorna o usuário autenticado (RNF02).

    O erro 401 com o header WWW-Authenticate segue a especificação
    HTTP para recursos protegidos por Bearer token (RFC 6750).
    """
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decodificar_token(token)
        email: str | None = payload.get("sub")
        if not email:
            raise credenciais_invalidas
    except JWTError:
        raise credenciais_invalidas

    usuario = db.query(UsuarioORM).filter(UsuarioORM.email == email).first()
    if not usuario:
        raise credenciais_invalidas

    return usuario
