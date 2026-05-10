---
name: Project Raízes do Nordeste
description: Contexto, regras de negócio, arquitetura e decisões do backend Raízes do Nordeste
type: project
---

Sistema de gestão de pedidos, estoque e fidelização para a rede "Raízes do Nordeste".

**Why:** Projeto multidisciplinar da Uninter — DESENVOLVIMENTO BACKEND 2026.

**How to apply:** Usar sempre a arquitetura em camadas (Domain → Application → Infrastructure → API) e nunca omitir o campo `canal_pedido` em modelos de pedido.

## Requisitos Funcionais
- RF01: Autenticação com perfis Admin, Atendente, Cozinha, Cliente
- RF02: Pedidos com `canal_pedido` obrigatório (APP, TOTEM, BALCAO, PICKUP, WEB)
- RF03: Status de pedido: RECEBIDO → PREPARANDO → PRONTO → ENTREGUE
- RF04: Pagamento mock (simula serviço externo, retorna Aprovado/Recusado)
- RF05: Controle de estoque por unidade local
- RF06: Fidelização com acúmulo e resgate de pontos

## Requisitos Não Funcionais
- RNF01: Senhas com BCrypt (passlib[bcrypt])
- RNF02: Autenticação JWT (python-jose[cryptography])
- RNF03: Arquitetura em camadas (Domain, Application, Infrastructure, API)
- RNF04: Swagger/OpenAPI em /docs e /redoc
- RNF05: LGPD — minimização e finalidade nos dados pessoais
- RNF06: Banco relacional com migrations (SQLAlchemy + Alembic)

## Estrutura de pastas
```
domain/          # Enums, Pydantic models (entidades puras)
application/     # Services, use cases, DTOs
infrastructure/  # SQLAlchemy ORM, repositórios, serviços externos
api/             # FastAPI routers, schemas de request/response
```

## Stack instalada (2026-05-10)
fastapi 0.136.1, uvicorn[standard] 0.46.0, sqlalchemy 2.0.49, pydantic 2.13.4,
alembic 1.18.4, python-jose 3.5.0, passlib 1.7.4, python-multipart 0.0.28

## Regra de Ouro
`CanalPedido` é um `str, Enum` em `domain/enums.py` — APP, TOTEM, BALCAO, PICKUP, WEB.
O campo `canal_pedido: CanalPedido` é **obrigatório** em toda entidade/schema de Pedido.
