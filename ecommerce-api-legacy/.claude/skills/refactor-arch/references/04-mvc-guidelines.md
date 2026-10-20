# Referência 04 — Guidelines de Arquitetura MVC (Alvo da Fase 3)

Objetivo: reestruturar o projeto para **MVC** com camadas claras, mantendo a stack e os endpoints originais.

## Estrutura-alvo

```
<projeto>/
├── config/            # configuração central (env-based; nada hardcoded)
│   └── settings.py(.js)
├── models/            # acesso a dados / entidades (sem HTTP, sem negócio de fluxo)
├── controllers/       # orquestram o fluxo: recebem request, chamam services/models, montam resposta
├── services/          # regras de negócio (podem ser por domínio)
├── views/ ou routes/  # apenas declaração de rotas (thin routing layer)
├── middlewares/       # error handler central, auth, etc.
└── app.py (ou src/app.js)  # entry point / composition root (application factory quando Flask)
```

Ajuste os nomes à convenção natural da stack — o que importa é a **separação de responsabilidades**, não os nomes exatos.

## Responsabilidades por camada

### Config (`config/`)
- Única fonte de configuração: porta, debug, chaves, caminhos de banco, credenciais.
- Lê de variáveis de ambiente com **defaults seguros** (`FLASK_DEBUG` default `false`, `SECRET_KEY` com fallback aleatório ou exigida por env).
- Fornece `.env.example` documentando as variáveis (sem valores reais).

### Models (`models/`)
- Abstraem dados: entidades, queries parametrizadas, mapeamento linha→objeto, serialização (`to_dict()` sanitizado — NUNCA expõe campos sensíveis como senha).
- Não conhecem HTTP (nada de `request`/`jsonify`/`req`/`res`).
- Domínio agrupado por entidade (`produto`, `usuario`, `pedido`, `task`...).

### Views/Routes (`views/` ou `routes/`)
- Apenas **declaram** as rotas e delegam para o controller.
- Sem lógica de negócio, sem SQL, sem validação pesada.
- Flask: `Blueprint`s por domínio. Express: `express.Router()` por domínio.

### Controllers (`controllers/`)
- Concentram o **fluxo da aplicação**: parse de request, validação de formato, chamada de service/model, montagem de resposta e status code.
- Sem SQL direto; regras de negócio complexas delegam para `services/`.
- Um controller por domínio (`produto_controller`, `pedido_controller`, `task_controller`...).

### Services (`services/`)
- Regras de negócio: cálculos, transações multi-passo, integrações, notificações.
- Reutilizáveis por controllers/rotas e testáveis em isolamento.
- Integrações externas (email etc.) encapsuladas aqui — nada de `print("ENVIANDO EMAIL")` nos controllers.

### Middlewares (`middlewares/`)
- **Error handling centralizado**: um handler global converte exceções em respostas JSON padronizadas (Flask: `@app.errorhandler`; Express: `(err, req, res, next)`).
- Auth/autorização (ex.: token de admin via env para endpoints sensíveis).
- Remove a necessidade de `try/except` repetido em cada handler (mantenha apenas onde há tratamento específico real).

### Entry point
- Claro e mínimo: cria app, registra camadas, sobe o servidor.
- Flask: application factory (`create_app()`) + `app.py` como composition root.
- Debug/porta vêm da config (defaults seguros).

## Regras de dependência

```
views → controllers → services → models → (banco)
                     ↘ config ↙
```

- Models não importam controllers/views.
- Controllers não importam views.
- Nada de estado global mutável para cache/conexão: encapsule (classes/serviços); conexão de banco gerenciada por um módulo `database`/`db` com funções de acesso.

## Checklist de aceite da Fase 3 (validação)

- [ ] Configuração extraída para módulo de config (sem hardcoded).
- [ ] Models criados/centralizados para abstrair dados.
- [ ] Views/Routes apenas roteiam.
- [ ] Controllers concentram o fluxo.
- [ ] Error handling centralizado.
- [ ] Entry point claro.
- [ ] Estrutura de diretórios segue o padrão MVC.
- [ ] Aplicação inicia sem erros.
- [ ] Todos os endpoints originais respondem (status + shape coerentes).

## Adaptação por stack

- **Python/Flask:** blueprints para rotas; `create_app`; `@app.errorhandler`; `werkzeug.security` para senhas.
- **Node/Express:** routers para rotas; middlewares de erro com 4 argumentos; módulos `require`/`export`; `crypto.scrypt`/`bcryptjs` para senhas; config via `process.env`.
- **Bancos em memória:** mantenha-os, mas garanta seeds no boot e integridade (cascade ao deletar).

## O que NÃO fazer na Fase 3

- Não trocar stack/banco/framework.
- Não remover endpoints (proteja-os se forem inseguros).
- Não reformatar código não relacionado.
- Não deixar `debug=True`/`0.0.0.0` hardcoded.
