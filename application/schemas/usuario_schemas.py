"""
Schemas Pydantic de entrada e saída dos endpoints de usuários.

Separamos UsuarioCreate de UsuarioResponse para nunca expor o hash
da senha nas respostas da API — princípio de minimização de dados (RNF05/LGPD).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from domain.enums import PerfilUsuario


class UsuarioCreate(BaseModel):
    """Dados necessários para cadastrar um novo usuário no sistema."""

    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=6, max_length=128)
    perfil: PerfilUsuario


class UsuarioResponse(BaseModel):
    """
    Dados retornados após cadastro ou consulta de usuário.

    O campo senha_hash é intencionalmente ausente aqui.
    """

    id: int
    nome: str
    email: str
    perfil: PerfilUsuario
    criado_em: Optional[datetime] = None

    # from_attributes permite construir o schema a partir de um objeto ORM
    model_config = {"from_attributes": True}
