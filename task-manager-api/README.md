# task-manager-api

API de Task Manager em Python/Flask, refatorada para a arquitetura **MVC** (desafio `refactor-arch`). A stack permanece: **Flask + Flask-SQLAlchemy + SQLite**.

## Estrutura (MVC)

```
task-manager-api/
├── config/            # configuração central (env-based; nada hardcoded)
│   └── settings.py
├── models/            # entidades + acesso a dados (serialização sanitizada)
├── controllers/       # fluxo request → service → resposta
├── services/          # regras de negócio, validação, serialização
├── routes/            # blueprints — apenas declaram rotas e delegam
├── middlewares/       # error handler central e auth (token de admin)
├── app.py             # application factory (composition root)
└── seed.py            # popula o banco com dados iniciais
```

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000` (porta/host/debug configuráveis via ambiente).

## Configuração (variáveis de ambiente)

Valores sensíveis **não** são hardcoded — vêm do ambiente com defaults seguros
(ver `config/settings.py`):

| Variável         | Default                  | Descrição                                        |
|------------------|--------------------------|--------------------------------------------------|
| `SECRET_KEY`     | aleatória por processo   | Chave usada para assinar o token de login        |
| `DATABASE_URL`   | `sqlite:///tasks.db`     | URI do banco                                     |
| `FLASK_DEBUG`    | `false`                  | Habilita o debugger do Flask                     |
| `HOST`           | `127.0.0.1`              | Interface de bind                               |
| `PORT`           | `5000`                   | Porta                                            |
| `ADMIN_TOKEN`    | `dev-admin-token`        | Token exigido nos endpoints destrutivos (DELETE) |
| `SMTP_HOST/PORT/USER/PASSWORD` | —            | SMTP opcional do serviço de notificação          |

## Autenticação

- **`POST /login`** devolve um **token assinado** (itsdangerous) no campo `token`
  (o antigo `fake-jwt-token-<id>` foi removido).
- Endpoints **destrutivos** (`DELETE /tasks/<id>`, `DELETE /users/<id>`,
  `DELETE /categories/<id>`) exigem o header `X-Admin-Token: <ADMIN_TOKEN>`.
- Senhas são armazenadas com **pbkdf2:sha256** (werkzeug); hashes legados MD5
  são migrados de forma transparente no primeiro login.

## Notas

- O `seed.py` popula o banco (`instance/tasks.db`) com usuários, categorias e
  tasks de exemplo — rode-o antes do primeiro boot.
- O hash de senha **nunca** é exposto nas respostas da API.
