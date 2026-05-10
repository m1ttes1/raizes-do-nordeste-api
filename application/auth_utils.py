"""
Funções de segurança para senhas e tokens JWT — RNF01 e RNF02.

O bcrypt protege as senhas em repouso: é lento por design, tornando
ataques de força bruta inviáveis mesmo após uma eventual exposição do banco.

O JWT (JSON Web Token) é utilizado para autenticação stateless conforme
o padrão OAuth2 com Password Flow: o servidor emite um token assinado
após o login bem-sucedido, e o cliente o reenvia em cada requisição.
Dessa forma, nenhuma sessão precisa ser armazenada no servidor, o que
facilita a escalabilidade e está alinhado com as boas práticas de
segurança exigidas pela LGPD (princípio de necessidade).
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

# Em produção, este valor deve vir de uma variável de ambiente (ex: os.getenv).
# Gerado via: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = "a3f8e2b1c9d74f6e2a8b5c1d7e9f3a2b4c6d8e0f1a3b5c7d9e1f3a5b7c9d1e3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# deprecated="auto" garante que hashes gerados por esquemas mais antigos
# sejam atualizados para bcrypt automaticamente no próximo login do usuário
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt da senha. O bcrypt já embute um salt aleatório."""
    return _pwd_context.hash(senha)


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Compara a senha recebida no login com o hash armazenado no banco."""
    return _pwd_context.verify(senha_plain, senha_hash)


def criar_token_acesso(dados: dict, expira_em: timedelta | None = None) -> str:
    """
    Gera um JWT assinado com os dados do usuário autenticado (RNF02).

    O campo 'sub' (subject) segue a especificação RFC 7519 e identifica
    o principal associado ao token — no nosso caso, o e-mail do usuário.
    """
    payload = dados.copy()
    expiracao = datetime.now(timezone.utc) + (
        expira_em or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expiracao
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str) -> dict:
    """
    Decodifica e valida um JWT recebido no cabeçalho Authorization.

    Lança JWTError se o token estiver malformado, com assinatura inválida
    ou já expirado — situações tratadas como 401 na camada de API.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
