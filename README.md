# 🚀 API-RPA | Coleta de Atos Normativos da Receita Federal

API em **FastAPI** integrada com um robô **RPA (Selenium)** para capturar atos normativos no portal da Receita Federal, enviar os dados via HTTP, persistir em **PostgreSQL**, oferecer **CRUD**, **dashboard agregado**, **logs de execução** e autenticação **JWT**.

## 📚 Sumário

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura](#2-arquitetura)
3. [Stack Tecnológica](#3--stack-tecnológica)
4. [Funcionalidades](#4--funcionalidades)
5. [Estrutura do Projeto](#5--estrutura-do-projeto)
6. [Pré-requisitos](#6--pré-requisitos)
7. [Variáveis de Ambiente](#7--variáveis-de-ambiente)
8. [Como Executar](#8--como-executar)
9. [Fluxo da Solução (RPA → API → Banco)](#9--fluxo-da-solução-rpa--api--banco)
10. [Autenticação JWT](#10--autenticação-jwt)
11. [Endpoints](#11-endpoints)
12. [Modelo de Dados](#12-modelo-de-dados)
13. [Logs](#13-logs)

---

## 1) Visão Geral

### 🎯 Objetivo do sistema

- Capturar atos normativos no site da Receita Federal
- Enviar os dados para uma API RESTful
- Persistir em banco SQL
- Implementar CRUD completo
- Registrar logs de execução do RPA
- Expor endpoint de dashboard com dados agregados
- Proteger endpoints sensíveis com JWT

---

## 2) Arquitetura

A aplicação está organizada em camadas:

- `routers/` → definição dos endpoints HTTP
- `services/` → regras de negócio e integração entre módulos
- `models/` → mapeamento ORM (SQLAlchemy)
- `schemas/` → contratos de entrada/saída (Pydantic)
- `database/` → sessão, engine e base declarativa
- `core/` → autenticação, configuração e scheduler
- `rpa/` → automação Selenium para coleta

### 🔄 Separação entre RPA e API

- O RPA coleta os dados no site externo
- O envio para persistência acontece pela API (`/atos/batch`), autenticado por JWT
- A API centraliza validação, deduplicação, persistência e logs

---

## 3) 🧰 Stack Tecnológica

- Python 3.11
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL 15
- Selenium 4 + Chromium/Chromedriver
- APScheduler
- JWT com `python-jose`
- Docker / Docker Compose

---

## 4) ⚙ Funcionalidades

- Coleta automatizada de atos normativos
- Inserção em lote com deduplicação por constraint única
- CRUD de atos
- Exclusão lógica com `deleted_at`
- Dashboard com agregação por órgão e tipo
- Execução manual e agendada do RPA
- Logs de execução consultáveis por endpoint
- Proteção JWT em rotas sensíveis

---

## 5) 📂 Estrutura do Projeto

```text
backend/app/
  core/
    auth.py
    scheduler.py
    security.py
    settings.py
  database/
    base.py
    deps.py
    session.py
  models/
    ato.py
    rpa_log.py
  routers/
    atos.py
    rpa.py
    logs.py
  rpa/
    scraper_selenium.py
  schemas/
    ato.py
    rpa_log.py
  services/
    ato_service.py
    rpa_service.py
  main.py
  Dockerfile
  docker-compose.yml
```

---

## 6) 🧩 Pré-requisitos

### 🐳 Com Docker (Recomendado)

- Docker  
- Docker Compose  

### 💻 Sem Docker

- Python 3.11+  
- PostgreSQL  
- Google Chrome instalado (ou Chromium compatível)  

---

## 7) 🔐 Variáveis de Ambiente

O projeto utiliza arquivos de ambiente separados por contexto de execução:

- `.env.local` → execução local (Windows / venv)  
- `.env.docker` → execução com Docker Compose  

Também é recomendado versionar exemplos:

- `.env.local.example`  
- `.env.docker.example`  

---

### 📁 `.env.local` (execução local)

```env
SECRET_KEY=sua_chave_jwt_forte
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname
API_BASE_URL=http://localhost:8000

RUNNING_IN_DOCKER=false
```

---

### 🐳 `.env.docker` (execução com Docker)

```env
SECRET_KEY=sua_chave_jwt_forte
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

DATABASE_URL=postgresql+psycopg2://user:pass@db:5432/dbname
API_BASE_URL=http://localhost:8000

RUNNING_IN_DOCKER=true

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=dbname
```

---

### ⚠ Observações Importantes

- Em execução local, o host do banco deve ser `localhost`.  
- Em Docker, o host do banco deve ser `db` (nome do serviço no Compose).  
- No `Settings` do Pydantic, manter `extra="ignore"` para evitar erro com variáveis extras do Postgres no mesmo `.env`.  

---

## 8) ▶ Como Executar

### 🐳 Docker

No diretório `backend/app`, configure o `docker-compose.yml` para usar `.env.docker` nos serviços `api` e `db`.

```bash
docker compose up --build
```

Acesse:

- API: http://localhost:8000  
- Swagger: http://localhost:8000/docs  

---

### 💻 Local (sem Docker)

Instale as dependências:

```bash
pip install -r backend/app/requirements.txt
```

No PowerShell, defina o arquivo de ambiente local e suba a API:

```powershell
$env:ENV_FILE=".env.local"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 9) 🔄 Fluxo da Solução (RPA → API → Banco)

1. O RPA autentica em `/auth/login`  
2. Coleta os atos normativos via Selenium  
3. Formata os dados no payload da API  
4. Envia lote para `/atos/batch` com token Bearer  
5. A API valida com Pydantic  
6. O serviço salva em lote com `ON CONFLICT DO NOTHING`  
7. A API grava log da execução em `rpa_logs`  

---

## 10) 🔑 Autenticação JWT

A autenticação utiliza `OAuth2PasswordBearer` com:

```
tokenUrl=/auth/login
```

### 📥 Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

**Body:**

```
username
password
```

**Resposta:**

```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

---

### 📤 Uso do Token

Enviar no header das requisições protegidas:

```http
Authorization: Bearer <access_token>
```

---

## 11) 📡 Endpoints

### 🔐 Auth

| Método | Endpoint | Descrição |
|--------|----------|------------|
| POST | `/auth/login` | Gera token JWT |

---

### 📄 Atos

| Método | Endpoint | Protegido | Descrição |
|--------|----------|------------|------------|
| POST | `/atos/` | ✅ | Cria ato unitário |
| POST | `/atos/batch` | ✅ | Insere lote de atos |
| GET | `/atos/` | ❌ | Lista atos com filtros (`data_inicio`, `data_fim`, `search`) |
| PUT | `/atos/{ato_id}` | ✅ | Atualiza ato |
| DELETE | `/atos/{ato_id}` | ✅ | Remove logicamente (`deleted_at`) |
| GET | `/atos/dashboard` | ❌ | Retorna agregados (`total_atos`, `por_orgao`, `por_tipo`) |

---

### 🤖 RPA

| Método | Endpoint | Protegido | Descrição |
|--------|----------|------------|------------|
| POST | `/rpa/executar` | ✅ | Executa RPA imediatamente |
| POST | `/rpa/schedule` | ✅ | Agenda execução por `interval` ou `cron` |
| GET | `/rpa/schedules` | ✅ | Lista agendamentos ativos |
| DELETE | `/rpa/schedule/{job_id}` | ✅ | Remove agendamento |

---

### 📑 Logs

| Método | Endpoint | Protegido | Descrição |
|--------|----------|------------|------------|
| GET | `/logs/rpa` | ✅ | Lista logs de execução do RPA com paginação e filtros |

#### Parâmetros recomendados

- `page` (default: 1)  
- `size` (default: 20)  
- `status` (opcional)  
- `data_inicio` (opcional)  
- `data_fim` (opcional)  

---

## 12) 🗂 Modelo de Dados

### 🗂 Tabela `atos`

| Campo | Tipo | Observação |
|-------|------|------------|
| id | UUID | PK |
| tipo_ato | string | |
| numero_ato | string | |
| orgao_unidade | string | |
| publicacao | date | |
| ementa | text | |
| created_at | datetime | |
| updated_at | datetime | |
| deleted_at | datetime | nullable (soft delete) |

**Constraint de unicidade:**

```
uq_ato_unico (numero_ato, publicacao, orgao_unidade)
```

---

### 🗂 Tabela `rpa_logs`

| Campo | Tipo | Observação |
|-------|------|------------|
| id | UUID | PK |
| execution_date | datetime | |
| total_registros | int | |
| status | string | |
| error_message | text | nullable |
| execution_time | float | segundos |

---

## 13) 📊 Logs

Cada execução de inserção em lote registra:

- Quantidade inserida  
- Status (`SUCESSO` / `ERRO`)  
- Mensagem de erro (quando houver)  
- Tempo de execução  

Consulta operacional via:

```http
GET /logs/rpa
```
