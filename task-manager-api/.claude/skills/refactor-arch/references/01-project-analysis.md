# Referência 01 — Heurísticas de Análise de Projeto (Fase 1)

Este documento ensina a skill a detectar **linguagem, framework, banco de dados, domínio e arquitetura atual** de qualquer projeto, de forma agnóstica de tecnologia.

## 1. Detecção da linguagem

| Evidência | Linguagem |
|---|---|
| Arquivos `.py`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile` | Python |
| Arquivos `.js`/`.mjs`/`.cjs`, `package.json`, `package-lock.json` | JavaScript (Node.js) |
| Arquivos `.ts`, `tsconfig.json` | TypeScript |
| Arquivos `.java`, `pom.xml`, `build.gradle` | Java |
| Arquivos `.go`, `go.mod` | Go |

Regras:
- Conte os arquivos fonte por extensão para confirmar a linguagem dominante (ex.: `find . -name "*.py" -not -path "*/venv/*" | wc -l`).
- Exclua sempre `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `dist/`, `build/`, `.git/` da contagem.
- Conte as linhas: `find . -name "*.py" ... | xargs wc -l` (ou equivalente).

## 2. Detecção do framework (e versão)

| Evidência no código | Evidência no manifesto | Framework |
|---|---|---|
| `from flask import ...`, `@app.route`, `Blueprint`, `app.add_url_rule`, `Flask(__name__)` | `flask==X.Y.Z` no requirements | Flask |
| `from fastapi import FastAPI`, `@app.get` | `fastapi` | FastAPI |
| `from django...`, `settings.py` | `django` | Django |
| `require('express')`, `app.get(`, `app.use(`, `express.Router()` | `"express": "^X"` no package.json | Express |
| `require('fastify')`, `fastify.` | `fastify` | Fastify |
| `require('koa')` | `koa` | Koa |

Versões: leia do manifesto (`requirements.txt` → `flask==3.1.1`; `package.json` → `"express": "^4.18.2"`). Se não houver versão fixada, reporte "não fixada".

## 3. Detecção do banco de dados

| Evidência | Banco / acesso |
|---|---|
| `sqlite3.connect(...)`, `new sqlite3.Database(...)`, arquivo `*.db`, `:memory:` | SQLite (direto) |
| `flask_sqlalchemy`, `SQLAlchemy(`, `db.Column(`, `db.Model` | SQLAlchemy / ORM (veja a URI) — `sqlite:///arquivo.db`, `postgresql://`, `mysql://` |
| `psycopg2`, `asyncpg` | PostgreSQL |
| `pymongo`, `mongoose` | MongoDB |
| `pool.query`, `mysql2` | MySQL |

Extraia também:
- **Tabelas**: procure `CREATE TABLE nome`, classes de model (`__tablename__`), chamadas `INSERT INTO x`. Liste os nomes.
- **Local do schema/seeds**: DDL embutida no código (ex.: dentro de `get_db()`), arquivos de migration, scripts `seed.py`, `initDb()`.

## 4. Mapeamento de arquitetura atual

Inspecione a árvore de diretórios e classifique:

| Organização | Sinais |
|---|---|
| Monolítica / sem camadas | Poucos arquivos grandes na raiz (`app.py`, `models.py`, `controllers.py` mas com tudo dentro); nenhuma pasta de camadas |
| Parcialmente organizada | Existem `models/`, `routes/`, `services/`, `utils/` mas com lógica misturada (rotas com negócio, modelos que acessam HTTP, duplicação) |
| Camadas (MVC/clean) | Separação clara: `models/`, `controllers/`, `views` ou `routes/`, `services/`, `config/`, `middlewares/` |

Perguntas a responder no resumo:
- Onde estão as rotas? (arquivo único vs blueprints/routers)
- Onde está a lógica de negócio? (controllers, rotas, models, scripts)
- Existe camada de configuração? (config central vs valores espalhados)
- Existe tratamento de erro centralizado? (vs `try/except` repetido em cada handler)
- Existe ponto de entrada claro? (`app.py` + `if __name__ == '__main__'`, `src/app.js` com `app.listen`)

## 5. Extração do inventário de endpoints

Padrões de busca por stack (guarde a lista: método + rota + handler + arquivo:linha):

- Flask: `@app.route(`, `@app.get/post/put/delete(`, `app.add_url_rule(`, `@bp.route(`, `@<blueprint>.route(`
- FastAPI: `@app.get(`, `@router.post(`
- Express: `app.get(`, `app.post(`, `app.put(`, `app.delete(`, `app.patch(`, `router.get(`, `router.post(`, etc.

## 6. Extração do domínio

- Leia o README do projeto (se existir).
- Infira do vocabulário: nomes de tabelas, rotas e models (ex.: `produtos, pedidos, usuarios` → "API de E-commerce"; `courses, enrollments, payments` → "LMS com checkout"; `tasks, categories` → "Task Manager").
- Descreva em uma linha: `<tipo> API (<entidades principais>)`.

## 7. Dados que a Fase 1 deve deixar prontos para as fases seguintes

1. Linguagem e framework/versão.
2. Lista de arquivos-fonte com linhas (para o relatório e contagem "~N lines of code").
3. Inventário de endpoints (para a validação da Fase 3).
4. Tabelas do banco e onde o schema é criado.
5. Classificação da arquitetura atual e camadas ausentes.
6. Domínio da aplicação em uma linha.
