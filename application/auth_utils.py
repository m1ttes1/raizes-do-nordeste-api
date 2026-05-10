"""
Funções de segurança para senhas — RNF01.

O bcrypt é escolhido por ser computacionalmente lento por design:
mesmo que o banco de dados seja comprometido, o atacante precisaria
de um tempo impraticável para descobrir as senhas originais.
"""
from passlib.context import CryptContext

# deprecated="auto" faz o passlib migrar hashes antigos para bcrypt
# automaticamente no próximo login do usuário, sem quebrar nada
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt da senha. O bcrypt já inclui salt aleatório."""
    return _pwd_context.hash(senha)


def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Compara a senha informada no login com o hash armazenado no banco."""
    return _pwd_context.verify(senha_plain, senha_hash)
