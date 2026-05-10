"""
Script de seed do banco de dados.

Popula o banco com usuários de teste e itens de cardápio para que
o avaliador possa testar todos os fluxos da API sem cadastros manuais.

Uso:
    python seeds.py
"""
from infrastructure.database import SessionLocal
from infrastructure.orm import ProdutoORM, UsuarioORM
from application.auth_utils import hash_senha


USUARIOS = [
    {
        "nome": "Admin Raízes",
        "email": "admin@raizes.com",
        "senha": "admin123",
        "perfil": "ADMIN",
    },
    {
        "nome": "Chef Nordestino",
        "email": "cozinha@raizes.com",
        "senha": "cozinha123",
        "perfil": "COZINHA",
    },
    {
        "nome": "João da Silva",
        "email": "cliente@raizes.com",
        "senha": "cliente123",
        "perfil": "CLIENTE",
    },
]

PRODUTOS = [
    {
        "nome": "Baião de Dois",
        "descricao": "Arroz com feijão-verde, queijo coalho, manteiga de garrafa e carne-seca desfiada. Prato típico cearense.",
        "preco": 28.90,
        "estoque": 30,
    },
    {
        "nome": "Carne de Sol na Chapa",
        "descricao": "Carne de sol artesanal acompanhada de macaxeira cozida, manteiga de garrafa e vinagrete.",
        "preco": 42.50,
        "estoque": 20,
    },
    {
        "nome": "Tapioca Nordestina",
        "descricao": "Tapioca crocante recheada com queijo coalho derretido, coco ralado e mel de engenho.",
        "preco": 14.00,
        "estoque": 50,
    },
    {
        "nome": "Buchada de Bode",
        "descricao": "Bucho de bode limpo, temperado com coentro, pimenta-de-cheiro e vinagre, cozido lentamente.",
        "preco": 35.00,
        "estoque": 15,
    },
    {
        "nome": "Sarapatel com Pirão",
        "descricao": "Sarapatel de porco temperado com pimenta-do-reino e cominho, servido com pirão de farinha de mandioca.",
        "preco": 38.00,
        "estoque": 18,
    },
]


def seed():
    db = SessionLocal()
    try:
        inseridos = {"usuarios": 0, "produtos": 0, "ignorados": 0}

        for dados in USUARIOS:
            ja_existe = db.query(UsuarioORM).filter_by(email=dados["email"]).first()
            if ja_existe:
                inseridos["ignorados"] += 1
                continue
            db.add(UsuarioORM(
                nome=dados["nome"],
                email=dados["email"],
                senha_hash=hash_senha(dados["senha"]),
                perfil=dados["perfil"],
            ))
            inseridos["usuarios"] += 1

        for dados in PRODUTOS:
            ja_existe = db.query(ProdutoORM).filter_by(nome=dados["nome"]).first()
            if ja_existe:
                inseridos["ignorados"] += 1
                continue
            db.add(ProdutoORM(
                nome=dados["nome"],
                descricao=dados["descricao"],
                preco=dados["preco"],
                estoque=dados["estoque"],
            ))
            inseridos["produtos"] += 1

        db.commit()

        print("Seed concluído.")
        print(f"  Usuários inseridos : {inseridos['usuarios']}")
        print(f"  Produtos inseridos : {inseridos['produtos']}")
        print(f"  Já existiam (ignorados): {inseridos['ignorados']}")
        print()
        print("Credenciais de acesso:")
        for u in USUARIOS:
            print(f"  [{u['perfil']:10}]  {u['email']}  /  senha: {u['senha']}")

    except Exception as exc:
        db.rollback()
        print(f"Erro durante o seed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
