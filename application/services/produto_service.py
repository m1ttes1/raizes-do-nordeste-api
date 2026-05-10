"""
Serviço de produtos — lógica de negócio do cardápio e do inventário (RF05).

Toda regra fica aqui; o router apenas traduz HTTP e o ORM apenas persiste.
As validações de integridade (preço positivo, estoque não-negativo) são
aplicadas no service além das constraints do Pydantic, garantindo que a
regra seja respeitada mesmo quando o service for chamado diretamente,
fora do contexto de uma requisição HTTP.
"""
from typing import List

from sqlalchemy.orm import Session

from application.schemas.produto_schemas import ProdutoCreate, ProdutoResponse, ProdutoUpdate
from infrastructure.orm import ProdutoORM


def criar_produto(db: Session, dados: ProdutoCreate) -> ProdutoResponse:
    """
    Cadastra um novo produto no cardápio (RF05).

    Lança ValueError se as regras de integridade forem violadas,
    embora o schema Pydantic já as aplique na camada de entrada.
    """
    if dados.preco <= 0:
        raise ValueError("O preço do produto deve ser maior que zero.")
    if dados.estoque < 0:
        raise ValueError("O estoque do produto não pode ser negativo.")

    produto_orm = ProdutoORM(
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
        estoque=dados.estoque,
    )
    db.add(produto_orm)
    db.commit()
    db.refresh(produto_orm)
    return ProdutoResponse.model_validate(produto_orm)


def listar_produtos(db: Session) -> List[ProdutoResponse]:
    """Retorna todos os produtos disponíveis no cardápio."""
    produtos = db.query(ProdutoORM).all()
    return [ProdutoResponse.model_validate(p) for p in produtos]


def atualizar_produto(
    db: Session, produto_id: int, dados: ProdutoUpdate
) -> ProdutoResponse:
    """
    Atualiza os dados de um produto existente (RF05).

    Aplica apenas os campos informados na requisição, preservando os demais.
    Lança ValueError se o produto não existir ou se as regras de integridade
    forem violadas (preço positivo, estoque não-negativo).
    """
    produto_orm = db.query(ProdutoORM).filter(ProdutoORM.id == produto_id).first()
    if not produto_orm:
        raise ValueError("Produto não encontrado.")

    if dados.preco is not None and dados.preco <= 0:
        raise ValueError("O preço do produto deve ser maior que zero.")
    if dados.estoque is not None and dados.estoque < 0:
        raise ValueError("O estoque do produto não pode ser negativo.")

    for campo, valor in dados.model_dump(exclude_none=True).items():
        setattr(produto_orm, campo, valor)

    db.commit()
    db.refresh(produto_orm)
    return ProdutoResponse.model_validate(produto_orm)


def deletar_produto(db: Session, produto_id: int) -> None:
    """
    Remove um produto do cardápio (RF05).

    Lança ValueError se o produto não existir.
    """
    produto_orm = db.query(ProdutoORM).filter(ProdutoORM.id == produto_id).first()
    if not produto_orm:
        raise ValueError("Produto não encontrado.")

    db.delete(produto_orm)
    db.commit()
