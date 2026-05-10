"""
Schemas Pydantic de entrada e saída dos endpoints de produtos (RF05).

ProdutoCreate e ProdutoUpdate separam as operações de escrita; ProdutoResponse
garante que a API exponha apenas os campos relevantes ao cliente, sem vazar
detalhes internos de persistência.
"""
from typing import Optional

from pydantic import BaseModel, Field


class ProdutoCreate(BaseModel):
    """Dados necessários para cadastrar um novo produto no cardápio."""

    nome: str = Field(min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    preco: float = Field(gt=0, description="Preço em reais; deve ser maior que zero.")
    estoque: int = Field(ge=0, description="Quantidade disponível; não pode ser negativa.")


class ProdutoUpdate(BaseModel):
    """
    Campos que podem ser alterados em um produto já cadastrado.

    Todos os campos são opcionais: apenas os informados na requisição
    serão atualizados, preservando os demais valores existentes.
    """

    nome: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    preco: Optional[float] = Field(default=None, gt=0)
    estoque: Optional[int] = Field(default=None, ge=0)


class ProdutoResponse(BaseModel):
    """Representação pública de um produto retornado pela API."""

    id: int
    nome: str
    descricao: Optional[str] = None
    preco: float
    estoque: int

    # from_attributes permite construir o schema a partir de um objeto ORM
    model_config = {"from_attributes": True}
