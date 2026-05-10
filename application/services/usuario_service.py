"""
Serviço de usuários — lógica de negócio do cadastro (RF01).

Toda regra fica aqui; o router só traduz HTTP e o ORM só persiste.
Essa separação facilita testar o comportamento sem subir o servidor.
"""
from sqlalchemy.orm import Session

from application.auth_utils import hash_senha
from application.schemas.usuario_schemas import UsuarioCreate, UsuarioResponse
from infrastructure.orm import UsuarioORM


def criar_usuario(db: Session, dados: UsuarioCreate) -> UsuarioResponse:
    """
    Cadastra um novo usuário com a senha protegida por bcrypt (RNF01).

    Lança ValueError se o e-mail informado já estiver em uso,
    pois e-mail é o identificador único de acesso ao sistema.
    """
    if db.query(UsuarioORM).filter(UsuarioORM.email == dados.email).first():
        raise ValueError("E-mail já cadastrado.")

    usuario_orm = UsuarioORM(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        perfil=dados.perfil.value,
    )
    db.add(usuario_orm)
    db.commit()
    db.refresh(usuario_orm)
    return UsuarioResponse.model_validate(usuario_orm)
