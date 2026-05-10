# Raízes do Nordeste API — Sistema de Gestão e Fidelização

Sistema de backend desenvolvido em Python para suportar as operações de uma rede de alimentação regional. A API centraliza a gestão multicanal de pedidos (aplicativo móvel, totem, balcão, pickup e web), o controle de estoque de produtos, o processamento de pagamentos e um motor de fidelização de clientes baseado em cashback.

---

## Arquitetura

O projeto adota uma **arquitetura em quatro camadas**, separando estritamente as responsabilidades de cada componente. Esta separação garante que a lógica de negócio seja independente do framework web e do banco de dados, facilitando a manutenção, os testes unitários e a eventual migração de tecnologia.

```
api/            → Apresentação: routers FastAPI, schemas de entrada e saída HTTP
application/    → Negócio: serviços, orquestrações, validações de caso de uso
domain/         → Regras puras: modelos Pydantic e enumerações (sem dependência de framework)
infrastructure/ → Persistência: engine SQLAlchemy, sessionmaker, modelos ORM
```

**Fluxo de dados:** A camada `api` invoca os serviços de `application`, que operam sobre os modelos de `domain` e delegam a persistência para `infrastructure`. A camada `domain` não importa nada das demais, garantindo máxima coesão e mínimo acoplamento.

---

## Tecnologias

| Tecnologia | Função |
|---|---|
| **Python 3.x** | Linguagem principal |
| **FastAPI** | Framework web assíncrono e geração automática de documentação |
| **SQLAlchemy** | ORM para mapeamento objeto-relacional e abstração do banco |
| **Pydantic V2** | Validação e serialização de dados com tipagem estrita |
| **Alembic** | Gerenciamento de migrações de esquema do banco de dados |
| **SQLite** | Banco de dados relacional de arquivo único para desenvolvimento |
| **python-jose** | Geração e validação de tokens JWT |
| **passlib / bcrypt** | Hash seguro de senhas |

---

## Destaques Técnicos

### Segurança com JWT e Controle de Acesso Baseado em Perfil (RBAC)

A autenticação utiliza o fluxo OAuth2 Password com tokens JWT assinados via algoritmo HS256. O payload do token carrega, além da identidade do usuário, o seu perfil (`ADMIN`, `ATENDENTE`, `COZINHA`, `CLIENTE`). Todas as rotas protegidas extraem e validam esse perfil antes de executar qualquer operação, implementando controle de acesso baseado em perfil (RBAC) de forma centralizada.

Exemplos de regras aplicadas:
- Criação, atualização e exclusão de produtos exigem perfil `ADMIN` ou `COZINHA`.
- Listagem de pedidos: perfis de gestão enxergam todos os pedidos; `CLIENTE` enxerga apenas os próprios.
- O pagamento de um pedido só pode ser iniciado pelo dono do pedido ou por um `ADMIN`.

As mensagens de erro de autenticação são intencionalmente genéricas — "E-mail ou senha inválidos" — para prevenir enumeração de usuários (anti-enumeration, alinhado à LGPD).

### Integridade de Estoque com Validação Transacional

Na criação de um pedido, o serviço realiza uma pré-validação completa de todos os itens — verificando existência do produto e disponibilidade de estoque — antes de persistir qualquer registro. Somente após essa validação atômica os registros são gravados e o estoque de cada produto é decrementado. Isso evita estados inconsistentes em que um pedido seria criado com itens indisponíveis.

### Motor de Fidelização por Cashback (RF06)

No momento da confirmação do pagamento, o sistema credita automaticamente pontos de fidelidade ao cliente, na proporção de 1 ponto por real pago. Os pontos são acumulados na tabela `fidelizacoes` e consultáveis via endpoint autenticado (`GET /usuarios/me/pontos`). O crédito só ocorre após a validação bem-sucedida do pagamento, garantindo que pontos indevidos nunca sejam concedidos.

---

## Como Executar

### Pré-requisitos

- Python 3.10 ou superior instalado
- Terminal com acesso ao diretório raiz do projeto

### 1. Criar e ativar o ambiente virtual

```powershell
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Aplicar as migrações do banco de dados

```bash
alembic upgrade head
```

Este comando criará o arquivo `raizes.db` e todas as tabelas necessárias.

### 4. Iniciar o servidor de desenvolvimento

```bash
uvicorn api.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

---

## Documentação Interativa

O FastAPI gera documentação interativa automaticamente a partir dos schemas e anotações de tipo do código:

| Interface | URL |
|---|---|
| **Swagger UI** (recomendado) | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` |

O Swagger UI permite autenticar com o botão **Authorize**, inserindo as credenciais de um usuário cadastrado para obter o token JWT e testar todos os endpoints protegidos diretamente pelo navegador.

---

## Endpoints Principais

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| `POST` | `/usuarios` | Cadastro de novo usuário | Público |
| `POST` | `/login` | Autenticação e emissão de token JWT | Público |
| `GET` | `/produtos` | Listagem do catálogo de produtos | Público |
| `POST` | `/produtos` | Cadastro de produto | ADMIN / COZINHA |
| `PUT` | `/produtos/{id}` | Atualização de produto | ADMIN / COZINHA |
| `DELETE` | `/produtos/{id}` | Remoção de produto | ADMIN / COZINHA |
| `POST` | `/pedidos` | Criação de pedido com baixa de estoque | Autenticado |
| `GET` | `/pedidos` | Listagem de pedidos (filtro por perfil) | Autenticado |
| `POST` | `/pedidos/{id}/pagar` | Registro de pagamento e crédito de pontos | Autenticado |
| `GET` | `/usuarios/me/pontos` | Consulta de saldo de pontos de fidelidade | Autenticado |

---

## Estrutura de Diretórios

```
.
├── alembic/              # Configuração e histórico de migrações
│   └── versions/
├── api/                  # Camada de apresentação
│   ├── main.py
│   ├── dependencies.py
│   └── routers/
│       ├── auth.py
│       ├── usuarios.py
│       ├── produtos.py
│       └── pedidos.py
├── application/          # Camada de negócio
│   ├── auth_utils.py
│   ├── schemas/
│   └── services/
├── domain/               # Modelos e regras de domínio puras
│   ├── enums.py
│   └── models.py
├── infrastructure/       # Camada de persistência
│   ├── database.py
│   └── orm.py
├── requirements.txt
└── alembic.ini
```

---

## Créditos

Desenvolvido por **Victor Mittestainer**  
Projeto Multidisciplinar — Desenvolvimento de Backend  
Uninter, 2026
