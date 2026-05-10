"""
Modelos ORM do SQLAlchemy — mapeamento entre as entidades do domínio
e as tabelas do banco de dados (RNF06).

Ficam separados de domain/models.py para não misturar regra de negócio
com detalhe de persistência, conforme a arquitetura em camadas (RNF03).
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))  # RNF01 — jamais texto puro
    perfil: Mapped[str] = mapped_column(String(20))
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    pedidos: Mapped[list["PedidoORM"]] = relationship(back_populates="cliente")
    fidelizacao: Mapped[Optional["FidelizacaoORM"]] = relationship(
        back_populates="cliente", uselist=False
    )


class ProdutoORM(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preco: Mapped[float] = mapped_column(Float)
    estoque: Mapped[int] = mapped_column(Integer, default=0)

    itens: Mapped[list["ItemPedidoORM"]] = relationship(back_populates="produto")


class PedidoORM(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    canal_pedido: Mapped[str] = mapped_column(String(10))  # RF02 — campo obrigatório
    status: Mapped[str] = mapped_column(String(20), default="RECEBIDO")
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cliente: Mapped["UsuarioORM"] = relationship(back_populates="pedidos")
    itens: Mapped[list["ItemPedidoORM"]] = relationship(back_populates="pedido")
    pagamento: Mapped[Optional["PagamentoORM"]] = relationship(
        back_populates="pedido", uselist=False
    )


class ItemPedidoORM(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"))
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"))
    quantidade: Mapped[int] = mapped_column(Integer)
    preco_unitario: Mapped[float] = mapped_column(Float)

    pedido: Mapped["PedidoORM"] = relationship(back_populates="itens")
    produto: Mapped["ProdutoORM"] = relationship(back_populates="itens")


class PagamentoORM(Base):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), unique=True)
    valor: Mapped[float] = mapped_column(Float)
    aprovado: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    processado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    pedido: Mapped["PedidoORM"] = relationship(back_populates="pagamento")


class FidelizacaoORM(Base):
    __tablename__ = "fidelizacoes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), unique=True)
    pontos_acumulados: Mapped[int] = mapped_column(Integer, default=0)

    cliente: Mapped["UsuarioORM"] = relationship(back_populates="fidelizacao")
