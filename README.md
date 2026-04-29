<h1 align="center">AIHOLD</h1>
<p align="center"><strong>Otimização de aportes Buy & Hold com Algoritmos Genéticos</strong></p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react&logoColor=000" />
  <img alt="Vite" src="https://img.shields.io/badge/Vite-Build-646CFF?logo=vite&logoColor=white" />
  <img alt="SQLite/PostgreSQL" src="https://img.shields.io/badge/DB-SQLite%20%7C%20PostgreSQL-336791?logo=postgresql&logoColor=white" />
</p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=cVOc9NlqDAY"><strong>Ver demonstração em vídeo</strong></a>
</p>

Projeto desenvolvido a partir do meu TCC **“AIHOLD: Otimização de Carteiras de Investimentos com Algoritmos Genéticos: Uma Abordagem para a Estratégia Buy and Hold”** (Ifes).

O AIHOLD resolve um problema prático do investidor Buy & Hold que ferramentas tradicionais normalmente ignoram: **como distribuir um aporte mensal fixo (ex.: R\$ 500) para manter a carteira próxima da alocação alvo, respeitando a indivisibilidade das cotas e minimizando sobra de caixa**.

- **TCC (página no repositório do Ifes)**: `https://repositorio.ifes.edu.br/handle/123456789/7437`
- **PDF (download direto)**: `https://repositorio.ifes.edu.br/server/api/core/bitstreams/795d77fc-5def-4f51-9118-faaaf9c510ba/content`

---

## Demonstração

- **Vídeo de uso do sistema**: `https://www.youtube.com/watch?v=cVOc9NlqDAY`

[![Demonstração AIHOLD](https://img.youtube.com/vi/cVOc9NlqDAY/maxresdefault.jpg)](https://www.youtube.com/watch?v=cVOc9NlqDAY)

---

## O que este sistema faz

- **Gerencia carteira** (ativos, quantidades, preços e metas de alocação).
- **Gera sugestões de compra** para um aporte informado usando:
  - **Algoritmo Genético** (principal, inspirado em evolução natural)
  - **Algoritmo determinístico (guloso)** como baseline de comparação
- **Integra cotações** via **Brapi** (B3).

### Intuição do Algoritmo Genético

O AG busca uma combinação de compras que otimiza simultaneamente:

- **Uso eficiente do aporte**: reduz o dinheiro parado (sobra).
- **Aderência por classe**: mantém o equilíbrio entre **Ações** e **FIIs**.
- **Aderência por ativo**: respeita as porcentagens alvo definidas para cada ticker.

---

## Stack

- **Backend**: Python + **FastAPI**
- **Frontend**: **React** + Vite
- **Banco**: **SQLite (padrão)** ou **PostgreSQL** (via `DATABASE_URL`)
- **Dados de mercado**: **Brapi**

---

## Como rodar (modo desenvolvimento)

### Pré-requisitos

- **Node.js** (recomendado 18+)
- **Python** (recomendado 3.10+)

> Observação: o backend roda com **SQLite por padrão**, então você consegue iniciar tudo sem Postgres.

---

### 1) Backend (FastAPI)

No diretório `AIHold-Back`:

1. Crie e ative um ambiente virtual.
2. Instale dependências.
3. Rode a API.

Exemplo (PowerShell):

```bash
cd AIHold-Back
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- **Healthcheck**: `GET http://localhost:8000/health`
- **Docs Swagger**: `http://localhost:8000/docs`

#### (Opcional) Popular banco com dados de exemplo

Com o backend parado ou rodando (tanto faz para o SQLite), execute:

```bash
cd AIHold-Back
.\.venv\Scripts\Activate.ps1
python scripts/init_db.py
```

Credenciais de teste criadas pelo seed:

- **username**: `admin`
- **senha**: `admin123`

---

### 2) Frontend (React + Vite)

No diretório `AIHold-Start`:

```bash
cd AIHold-Start
npm install
npm run dev
```

O frontend usa a variável:

- `VITE_API_URL` (arquivo `AIHold-Start/.env`)  
  valor atual: `http://localhost:8000`

---

## Endpoints principais (resumo)

- **Auth**
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `GET /api/auth/me`
- **Sugestões de aporte**
  - `GET /api/investimentos/sugestoes?valor_aporte=500&algoritmo=genetico`
  - `GET /api/investimentos/sugestoes?valor_aporte=500&algoritmo=deterministico`

> Nota: as porcentagens ideais precisam somar **100% dentro de cada classe** (Ações e FIIs).

---

## Banco de Dados

Por padrão, o backend usa:

- `sqlite:///./aihold.db` (criado automaticamente)

Se quiser PostgreSQL, defina:

- `DATABASE_URL="postgresql://user:password@localhost:5432/dbname"`

---

## Sobre o TCC (base científica)

Este projeto é fruto do TCC apresentado ao **Instituto Federal do Espírito Santo (Ifes)**, demonstrando uma aplicação prática de IA em finanças pessoais para resolver a **logística operacional do rebalanceamento via aportes mensais**.

Nos experimentos descritos no trabalho, o modelo com Algoritmos Genéticos obteve:

- **Melhoria de ~19%** em qualidade de alocação (fitness) vs. algoritmo guloso.
- **Fitness médio ~0,97**, aproximando a carteira real da planejada.
- **Tempo médio < 500ms** mesmo em carteiras diversificadas.

Referências do trabalho:

- Página do TCC: `https://repositorio.ifes.edu.br/handle/123456789/7437`
- PDF: `https://repositorio.ifes.edu.br/server/api/core/bitstreams/795d77fc-5def-4f51-9118-faaaf9c510ba/content`

---

## Como citar

Se este projeto te ajudou em pesquisa/estudo, cite o TCC via o repositório do Ifes:

- `https://repositorio.ifes.edu.br/handle/123456789/7437`


