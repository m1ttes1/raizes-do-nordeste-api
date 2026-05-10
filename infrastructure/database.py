"""
Configuração da sessão com o banco de dados via SQLAlchemy.

A variável Base é importada pelos modelos ORM para registrar as tabelas
e pelo Alembic para detectar mudanças e gerar as migrations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./raizes.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # check_same_thread=False é necessário porque o SQLite, por padrão,
    # só permite uso na thread que o criou, e o FastAPI usa múltiplas threads
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI que fornece uma sessão de banco por requisição.

    Usa o padrão generator para garantir que a sessão seja fechada
    mesmo se a rota lançar uma exceção.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
