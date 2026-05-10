"""
Schemas de autenticação — entrada do login e resposta com o token.

O TokenResponse segue o formato definido pela especificação OAuth2
(RFC 6749): o campo token_type deve ser 'bearer' para que os clientes
saibam como enviar o token nos cabeçalhos das requisições subsequentes.
"""
from pydantic import BaseModel, Field


class LoginInput(BaseModel):
    """Credenciais informadas pelo usuário para autenticação."""

    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    """
    Token de acesso retornado após login bem-sucedido.

    O cliente deve enviar o access_token no cabeçalho de cada
    requisição protegida: Authorization: Bearer <token>.
    """

    access_token: str
    token_type: str = "bearer"
