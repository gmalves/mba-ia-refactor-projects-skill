# Criação de Skills — Refatoração Arquitetural Automatizada

> Desafio técnico do **MBA em Engenharia de Software com IA (Full Cycle)**.
> O projeto entrega a skill **`refactor-arch`** — uma skill agêntica (Claude Code) que audita e refatora projetos legados para o padrão **MVC**, em 3 fases, de forma **agnóstica de tecnologia** — e a execução dela em 3 projetos legados fornecidos (2× Python/Flask + 1× Node.js/Express), com relatórios de auditoria, código refatorado e validações.

## Estrutura do repositório

```
mba-ia-refactor-projects-skill/
├── README.md                              # Esta documentação (Análise Manual, Construção da Skill, Resultados, Como Executar)
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (E-commerce) — refatorado em MVC
│   ├── .claude/skills/refactor-arch/      # ← A SKILL (SKILL.md + 5 arquivos de referência)
│   ├── .env.example
│   └── app.py, config/, models/, services/, controllers/, routes/, middlewares/, schema.py, database.py
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS + checkout) — refatorado em MVC
│   ├── .claude/skills/refactor-arch/      # ← CÓPIA DA SKILL
│   ├── .env.example
│   └── src/{config,models,services,controllers,routes,middlewares,utils}/, src/app.js, src/database.js
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (Task Manager) — refatorado em MVC
│   ├── .claude/skills/refactor-arch/      # ← CÓPIA DA SKILL
│   └── ...
│
├── reports/                               # Relatórios da Fase 2 (auditoria) de cada projeto
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
│
└── logs/                                  # Evidências de validação pós-refatoração (Fase 3)
    ├── project-1-validation.txt
    ├── project-2-validation.txt
    └── project-3-validation.txt
```

A skill é **componente versionado**: além de viver dentro de cada projeto (`.claude/skills/refactor-arch/`), seu conteúdo é idêntico nos 3 projetos — cópia direta, exatamente como pede o desafio (skill "copiável").

---

## A) Análise Manual

Antes de criar a skill, os 3 projetos foram lidos linha a linha e os problemas foram catalogados (severidade, arquivo:linha, justificativa). Os achados abaixo guiaram diretamente o catálogo de anti-patterns da skill.

### Projeto 1 — code-smells-project (Python/Flask — API de E-commerce)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection generalizada: queries montadas por concatenação de strings com dados do usuário | models.py (28, 48-50, 57-60, 68, 92, 109-111, 126-129, 140, 148-166, 174, 188-192, 220-224, 279-297) | Permite bypass de login (`' OR '1'='1`), exfiltração e destruição de dados em TODAS as operações |
| 2 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário enviado pelo cliente, sem autenticação | app.py:59-78 | Execução arbitrária de SQL: leitura/escrita/destruição total do banco por qualquer um |
| 3 | CRITICAL | Endpoint `/admin/reset-db` apaga todas as tabelas, sem autenticação | app.py:47-57 | Qualquer cliente pode zerar a base inteira (perda de dados) |
| 4 | CRITICAL | SECRET_KEY hardcoded e vazada publicamente no `/health` | app.py:7; controllers.py:289 | Segredo no repositório + exposto em endpoint; permite forjar assinaturas |
| 5 | CRITICAL | Senhas em texto puro no banco, comparadas em SQL, e devolvidas pela API (`senha` no JSON) | models.py:83, 99, 105-120; database.py:76-78 | Vazamento de credenciais; comprometimento total de contas |
| 6 | HIGH | God File: models.py concentra dados + regras + relatórios; controllers.py mistura validação + negócio + "notificações" | models.py:1-314; controllers.py:1-292 | Impossível testar em isolamento; qualquer mudança afeta tudo (viola SRP/MVC) |
| 7 | HIGH | Debug mode ativo + bind em 0.0.0.0 | app.py:88 | Debugger do Werkzeug = RCE; app acessível em todas as interfaces |
| 8 | MEDIUM | N+1 aninhado: para cada pedido consulta itens; para cada item consulta o produto | models.py:171-233 | Performance degrada linearmente com o volume |
| 9 | MEDIUM | Sem rollback/transação nos fluxos multi-passo; conexão global compartilhada (`check_same_thread=False`) | database.py:4-11; models.py:133-169 | Banco inconsistente em falhas parciais; corrida entre requisições |
| 10 | MEDIUM | "Notificações" que são só `print` (EMAIL/SMS/PUSH); cancelamento não devolve estoque | controllers.py:208-210, 249-250 | Efeitos colaterais falsos; regra de negócio incompleta |
| 11 | LOW | Magic numbers (faixas de desconto, taxas, porta, limites) | models.py:256-262 | Legibilidade/manutenção; mudança de regra exige caçar o número |
| 12 | LOW | Duplicação de mapeamento linha→dict (3×) e funções quase idênticas | models.py:9-21, 31-40, 171-233 | Correções precisam ser feitas N vezes; divergência de comportamento |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS com checkout)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais de produção hardcoded no config (dbPass, paymentGatewayKey `pk_live_...`) | src/utils.js:1-7 | Segredos no repositório; rotação exige alterar código |
| 2 | CRITICAL | Log do checkout imprime o número do cartão E a chave do gateway | src/AppManager.js:45 | Vazamento de dados de cartão (PCI-DSS) e do segredo de pagamento |
| 3 | CRITICAL | "Hash" caseiro de senha (loop de base64, 10 chars, sem salt) + senha default `123456` e seed `123` em texto puro | src/utils.js:17-23; src/AppManager.js:18, 68 | Senhas trivialmente quebráveis; comprometimento de contas |
| 4 | CRITICAL | `/api/admin/financial-report` e `DELETE /api/users/:id` sem autenticação | src/AppManager.js:80, 131 | Qualquer um lê dados financeiros/estudantes e apaga usuários |
| 5 | HIGH | God Class: AppManager inicializa banco + seeds + rotas + checkout + relatório | src/AppManager.js:4-139 | Sem camadas; baixa coesão; difícil testar/manter |
| 6 | HIGH | Estado global mutável (`globalCache`, `totalRevenue` — este morto) | src/utils.js:9-10 | Bugs de concorrência; memória cresce sem controle |
| 7 | MEDIUM | N+1 em cascata no relatório financeiro (3 níveis de loops + queries por item, sem tratamento de erro interno) | src/AppManager.js:89-127 | Performance e complexidade (callback pyramid) |
| 8 | MEDIUM | Exclusão de usuário sem cascade: matrículas/pagamentos ficam órfãos (o próprio código admite) | src/AppManager.js:131-137 | Banco inconsistente; relatórios errados |
| 9 | MEDIUM | Validação superficial (só presença) + pagamento "fake" (`cc.startsWith("4")`) | src/AppManager.js:35, 46 | Dados inválidos; lógica de pagamento obscura |
| 10 | LOW | Nomes crípticos (`u`, `e`, `p`, `cid`, `cc`), magic string `"4"`, `console.log` como logging | src/AppManager.js:29-33, 46; src/utils.js:12-15 | Legibilidade e manutenção ruins |
| 11 | LOW | Dependências desatualizadas (express ^4.18; linha 4.x em manutenção) e API de callback do sqlite3 | package.json:10-11 | Oportunidade de modernização (promises/async-await) |

### Projeto 3 — task-manager-api (Python/Flask — API de Task Manager)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | Senhas com MD5 sem salt | models/user.py:27-32 | Hash quebrável (rainbow tables); comprometimento de contas |
| 2 | CRITICAL | Campo `password` (hash) incluído em TODAS as respostas de API (`to_dict` + login) | models/user.py:16-25; user_routes.py:33, 85, 129, 209 | Exposição de credenciais pela própria API |
| 3 | HIGH | Credenciais hardcoded: senha SMTP no serviço de notificação e SECRET_KEY no app | services/notification_service.py:9-10; app.py:13 | Segredos no repositório; e-mail comprometível |
| 4 | HIGH | Nenhuma autenticação/autorização; login devolve `fake-jwt-token-<id>`; role admin nunca verificada | user_routes.py:207-210 | Auth quebrada por design; escalada de privilégio |
| 5 | MEDIUM | APIs deprecated: `datetime.utcnow()` (~15 ocorrências) e `Model.query.get()` (legacy SQLAlchemy 2.0) | models/task.py:15-16; routes/*.py; seed.py; helpers.py | Warnings e remoção futura; datas naive |
| 6 | MEDIUM | N+1 sistêmico: queries por task (user/category), por usuário e por categoria em loops | task_routes.py:41-57, 273-299; report_routes.py:53-68, 163 | Performance degrada com volume |
| 7 | MEDIUM | Duplicação: serialização task→dict em 3 lugares; lista de status válidos em 5 pontos; `process_task_data` morto | task_routes.py:17-59, 163-181; helpers.py:57-108 | Correções N vezes; divergência |
| 8 | MEDIUM | Código morto: imports não usados; `NotificationService` nunca invocado; notificações em memória | app.py:7; task_routes.py:7; services/notification_service.py | Ruído; funcionalidade "existente" que nunca roda |
| 9 | LOW | `except:` nu engolindo exceções; mensagens de erro genéricas | task_routes.py:62, 137, 236; helpers.py:46-49 | Bugs silenciosos |
| 10 | LOW | `type(x) == list`, senha mínima de 4 chars, debug+0.0.0.0 e URI do banco hardcoded | helpers.py:103; user_routes.py:64; app.py:11, 34 | Qualidade/configuração |
| 11 | LOW | Constantes espalhadas no fim do arquivo; validações fora de camada única | helpers.py:110-116 | Organização |

---

## B) Construção da Skill

### Decisões de design (SKILL.md e arquivos de referência)

- **SKILL.md é o maestro, não a enciclopédia**: ele define o contrato de execução (3 fases sequenciais, golden rules, formato de saída, critérios de validação) e delega TODO o conhecimento de domínio para os arquivos de referência, lidos sob demanda por fase. Isso mantém o prompt principal curto e permite evoluir o conhecimento sem tocar no contrato.
- **5 arquivos de referência** (uma área de conhecimento por arquivo, como exige o desafio):
  1. `references/01-project-analysis.md` — heurísticas de detecção de linguagem, framework, banco, arquitetura e endpoints;
  2. `references/02-anti-pattern-catalog.md` — catálogo com **15 anti-patterns** (sinais de detecção, severidade, impacto) incluindo uma seção específica de **APIs deprecated** com tabela de equivalentes modernos;
  3. `references/03-audit-report-template.md` — template exato do relatório da Fase 2 (+ regras: ordering por severidade, arquivo:linha exatos, mínimo de findings);
  4. `references/04-mvc-guidelines.md` — estrutura MVC-alvo, responsabilidade de cada camada, regras de dependência e adaptação por stack;
  5. `references/05-refactoring-playbook.md` — **13 padrões de transformação** com código antes/depois, na ordem de aplicação sugerida.
- **Golden rules no topo do SKILL.md**: read-only até a confirmação; preservar stack; preservar contratos dos endpoints; validar boot+endpoints antes de declarar sucesso. São as regras que impedem o comportamento mais perigoso de um agente refatorador (quebrar o app ou sair mudando tudo).
- **Gate obrigatório na Fase 2**: o SKILL.md termina a fase com o bloco literal
  `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` e a instrução explícita de **não tocar em nenhum arquivo até o `y`**.

### Catálogo de anti-patterns — o que entrou e por quê

Os 15 anti-patterns cobrem exatamente as classes de problema encontradas na análise manual dos 3 projetos (o que garante ≥5 findings por projeto), mas foram escritos de forma **genérica o suficiente para outros projetos**:

| AP | Nome | Sev. |
|---|---|---|
| AP-01 | SQL Injection (queries concatenadas) | CRITICAL |
| AP-02 | Credenciais/segredos hardcoded | CRITICAL |
| AP-03 | Exposição de dados sensíveis (serialização, logs, endpoints abertos) | CRITICAL |
| AP-04 | Armazenamento de senha inseguro (plaintext/MD5/hash caseiro) | CRITICAL |
| AP-05 | God Class / God File / God Method | CRITICAL |
| AP-06 | Auth/authz ausente em endpoints sensíveis | CRITICAL/HIGH |
| AP-07 | Regras de negócio em controllers/rotas + integrações falsas | HIGH |
| AP-08 | Config insegura / debug em produção | HIGH |
| AP-09 | Estado global mutável | HIGH |
| AP-10 | Integridade: sem cascade/transação, fluxos incompletos | HIGH |
| AP-11 | N+1 (query em loop) | MEDIUM |
| AP-12 | Validação de entrada superficial | MEDIUM |
| AP-13 | Duplicação de código/serialização | MEDIUM |
| AP-14 | **APIs deprecated** (utcnow, Query.get, before_first_request, new Buffer, url.parse, body-parser, request, app.del, var, callbacks fs) | MEDIUM |
| AP-15 | Magic numbers/strings, nomenclatura, logging improvisado | LOW |

### Como a skill foi mantida agnóstica de tecnologia

- **Detecção por evidências, não por nomes fixos**: o `01` mapeia extensões/manifests/imports → linguagem/framework, com tabelas que cobrem Flask/FastAPI/Django/Express/Fastify/Koa.
- **Camadas descritas semanticamente** (o que cada camada DEVE fazer), com adaptação explícita por stack no `04` (blueprints Flask vs routers Express).
- **Playbook com exemplos nas duas stacks** (Python e Node) em todas as transformações relevantes (§1, §2, §3, §9, §11, §12).
- **Validação dirigida por stack**: o SKILL.md define o princípio (boot + exercitar todos os endpoints) e o agente adapta o como (venv/pip vs npm/node).
- Prova final: os 3 projetos têm stacks/organizações diferentes e a skill executou nas 3 **sem nenhuma alteração** entre execuções.

### Desafios encontrados e como foram resolvidos

1. **Pausa obrigatória da Fase 2 (confirmar antes da Fase 3) em execução headless**: o desafio exige o gate humano, mas `claude -p` não tem entrada interativa. **Solução**: fluxo em duas execuções encadeadas — `claude -p "/refactor-arch"` roda as Fases 1–2 e encerra no gate; após revisão do relatório, `claude -c -p "y"` continua a MESMA sessão e executa a Fase 3. O gate aparece literalmente no log e controla a execução.
2. **Blocos de "thinking" muito longos na retomada do Projeto 3**: o modelo do ambiente (deepseek-v4-pro atrás de um gateway corporativo) emite blocos de raciocínio interno extremamente longos (até ~45k tokens — comportamento normal, observado também nas execuções bem-sucedidas) antes de emitir cada mensagem. Na retomada da sessão do P3, a primeira tentativa ficou >7 min sem emitir nenhuma mensagem e foi interrompida. **Solução**: a Fase 3 do P3 foi relançada numa sessão NOVA com um prompt focado ("Fase 2 já aprovada; execute a Fase 3 lendo SKILL.md + references/04 + /05"), lendo o relatório já gravado em `reports/`. A skill em si não mudou; apenas o mecanismo de retomada foi ajustado.
3. **Hooks/permissões do ambiente bloqueando comandos amplos**: um hook do ambiente do usuário bloqueou `find` irrestrito durante a Fase 1 de um dos projetos — o agente adaptou para listagens escopadas (sem intervenção).
4. **Escrita de `.env.example` bloqueada dentro do Claude Code** (regra de permissão do ambiente para arquivos `.env*`): as variáveis ficam documentadas em `config/settings.py`; os `.env.example` dos projetos foram criados fora da sessão agêntica e commitados junto.
5. **Python 3.9 (ambiente local) sem `hashlib.scrypt`**: o Werkzeug usaria scrypt por default e falharia; o agente detectou no boot e fixou `pbkdf2:sha256` (com salt) — decisão tomada e executada autonomamente pela skill durante a Fase 3.

---

## C) Resultados

### Resumo dos relatórios de auditoria (Fase 2)

| Projeto | Stack | Arquivos | Endpoints | Findings | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|---|---|---|---|
| code-smells-project | Python + Flask 3.1.1 | 4 (~780 LOC) | 19 | **17** | 6 | 5 | 3 | 3 |
| ecommerce-api-legacy | Node.js + Express ^4.18 | 3 (~180 LOC) | 3 | **11** | 5 | 3 | 2 | 1 |
| task-manager-api | Python + Flask 3.0.0 (+SQLAlchemy) | 15 (~1158 LOC) | 22 | **12** | 4 | 3 | 4 | 1 |

Relatórios completos (saída verbatim da Fase 2): [`reports/audit-project-1.md`](reports/audit-project-1.md), [`reports/audit-project-2.md`](reports/audit-project-2.md), [`reports/audit-project-3.md`](reports/audit-project-3.md).

### Comparação antes/depois da estrutura

**Projeto 1 — code-smells-project (Python/Flask)**

```
ANTES (monolito)                     DEPOIS (MVC — 25 arquivos)
app.py            (rotas+admin+db)   app.py                       # factory/composition root
controllers.py    (292 linhas)       config/settings.py           # env-based, sem hardcoded
models.py         (314 linhas)       database.py + schema.py      # conexão por request + DDL/seeds
database.py       (conexão+schema+   models/{produto,usuario,pedido}_model.py
                   seeds)            services/{produto,usuario,pedido,relatorio,notificacao}_service.py + errors.py
requirements.txt                     controllers/{produto,usuario,pedido,relatorio,admin,geral}_controller.py
                                     routes/{produtos,usuarios,pedidos,relatorios,admin,geral}.py  # blueprints finos
                                     middlewares/{auth,error_handler}.py
```

**Projeto 2 — ecommerce-api-legacy (Node/Express)**

```
ANTES (God Class)                    DEPOIS (MVC)
src/app.js        (14 linhas)        src/app.js                   # composition root
src/AppManager.js (banco+seeds+      src/config/settings.js       # env-based
                   rotas+negócio+    src/database.js              # conexão+DDL+seeds+withTransaction
                   relatórios)       src/models/{user,course,enrollment,payment,audit,report}Model.js
src/utils.js      (config+crypto+    src/services/{checkout,report}Service.js
                   cache global)     src/controllers/{checkout,report,user}Controller.js
package.json                         src/routes/{index,checkout,admin,user}Routes.js
                                     src/middlewares/{auth,errorHandler}.js
                                     src/utils/{AppError,password}.js
```

**Projeto 3 — task-manager-api (Python/Flask — organização parcial)**

```
ANTES (parcial)                      DEPOIS (MVC)
app.py  seed.py  database.py         app.py                   # application factory
models/ (3)  routes/ (3)             config/settings.py       # env-based, sem hardcoded
services/ (morto)  utils/ (morto)    models/ (3, sanitizados; pbkdf2; timezone.utc)
                                     controllers/ (5)         # fluxo por domínio
                                     services/ (10)           # auth (token itsdangerous), validators,
                                                              # serializers, time_utils, reports (GROUP BY)...
                                     routes/ (6, finos) + middlewares/{auth,error_handler}
                                     utils/ REMOVIDO (dead code)
```

### Checklist de validação (por projeto)

**code-smells-project (P1):**

```
Fase 1 — Análise
[x] Linguagem detectada corretamente (Python)
[x] Framework detectado corretamente (Flask 3.1.1 + flask-cors 5.0.1)
[x] Domínio descrito corretamente (API de E-commerce: produtos, usuários, pedidos)
[x] Número de arquivos condiz com a realidade (4 arquivos, ~780 linhas, 19 endpoints)

Fase 2 — Auditoria
[x] Relatório segue o template (references/03)
[x] Cada finding tem arquivo e linhas exatos
[x] Findings ordenados por severidade (CRITICAL → LOW)
[x] Mínimo de 5 findings (17)
[x] Deprecated check aplicado ("Nenhuma API deprecated encontrada" — explicitado)
[x] Skill pausou e pediu confirmação antes da Fase 3

Fase 3 — Refatoração
[x] Estrutura de diretórios MVC
[x] Configuração extraída (config/settings.py + .env.example; sem hardcoded)
[x] Models abstraindo dados (3 models + JOIN parametrizado)
[x] Views/Routes separadas (6 blueprints finos)
[x] Controllers concentrando o fluxo (6 controllers)
[x] Error handling centralizado (middlewares/error_handler.py)
[x] Entry point claro (app.py, application factory)
[x] Aplicação inicia sem erros
[x] Endpoints originais respondem (19/19; ver logs/project-1-validation.txt)
```

**ecommerce-api-legacy (P2):** mesmo checklist — `[x]` em todos os itens; validações de destaque: auth de admin (401 sem token / 200 com `X-Admin-Token`), checkout 200/400 (recusa e validação), exclusão com cascade comprovada (receita caiu de 997 → 0 após deletar o usuário, sem órfãos) — ver `logs/project-2-validation.txt`.

**task-manager-api (P3):** mesmo checklist — `[x]` em todos os itens; validações registradas em `logs/project-3-validation.txt` (boot + bateria de endpoints: tasks CRUD, users, categorias, relatórios, busca, stats, login).

### Evidências de aplicações rodando após refatoração

- P1: `logs/project-1-validation.txt` — `/health` (200, sem segredos), `/produtos` (200), busca (200), `/login` (200, pbkdf2 com upgrade transparente), `/pedidos` (201; quantidade negativa → 400 de validação), 404, `/admin/query` (401 sem token; 200 SELECT com token; DDL rejeitado — ver saída da Fase 3).
- P2: `logs/project-2-validation.txt` — relatório financeiro (401/200), checkout (200/400/400), delete (401/200 com cascade).
- P3: `logs/project-3-validation.txt` — boot e bateria completa de endpoints.

### Observações sobre o comportamento da skill em stacks diferentes

- **Mesma skill, mesmo contrato, execuções independentes** nos 3 projetos — nenhuma adaptação de SKILL.md/refs entre execuções.
- **Monolito (P1/P2)**: a Fase 3 aplicou decomposição total (mais transformações estruturais).
- **Organização parcial (P3)**: a skill corretamente NÃO jogou o projeto no lixo — manteve a organização existente e adequou (conectou services/controllers, removeu código morto, centralizou erro, modernizou deprecated). Exatamente o comportamento "adapte ao contexto" esperado.
- **Tamanhos diferentes, mesma qualidade**: os banners da Fase 1 detectaram endpoints e tabelas corretamente nos 3 (19/3/22 endpoints; 4/5/3 tabelas).

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (`claude --version`); qualquer conta/modelo que responda no seu ambiente.
  - _Neste ambiente o Claude Code está conectado a um gateway corporativo (GenPlat, modelos deepseek) — a skill não depende disso._
- **Python 3.9+** (para os projetos Flask) e **Node.js 18+** (para o projeto Express).
- A skill NÃO requer dependências extras: usa apenas o que o ambiente agêntico oferece (leitura/escrita de arquivos, terminal).

### Execução (ordem sugerida)

```bash
# Projeto 1 — Python/Flask
cd code-smells-project
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
claude "/refactor-arch"          # Fases 1 e 2 (pausa no gate)

# — revise reports/audit-project-1.md e confirme (y) na sessão —

# Projeto 2 — Node/Express
cd ../ecommerce-api-legacy
npm install
claude "/refactor-arch"

# Projeto 3 — Python/Flask (organização parcial)
cd ../task-manager-api
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
python seed.py
claude "/refactor-arch"
```

Em ambientes **headless/automatizados** (como o usado para gerar este entregável), o gate da Fase 2 é operado em duas execuções: a primeira roda as Fases 1–2 (`claude -p "/refactor-arch"`), e a confirmação segue com a retomada da sessão (`claude -c -p "y"`).

### Como validar que a refatoração funcionou

```bash
# 1) O app sobe?
python app.py            # Flask   — ou: node src/app.js   (Express)

# 2) Os endpoints originais respondem? (exemplos; lista completa em reports/)
curl -s localhost:5000/health
curl -s localhost:5000/tasks
curl -s -X POST localhost:5000/login -H 'Content-Type: application/json' \
     -d '{"email":"joao@email.com","password":"1234"}'

# 3) A validação automática da própria skill (Fase 3) executa boot + bateria
#    completa de endpoints e imprime o banner com o resultado.
```

Arquivos de referência da execução completa (logs/relatórios) estão listados na seção **Resultados**.

---

## Conformidade com os critérios de aceite

| Critério | Requisito | Resultado |
|---|---|---|
| Fase 1 detecta stack corretamente | 3/3 obrigatório | ✅ 3/3 (banners: Flask 3.1.1 / Express ^4.18 / Flask 3.0.0 + SQLAlchemy) |
| Fase 2 encontra ≥ 5 findings | 3/3 obrigatório | ✅ 17 / 11 / 12 |
| Fase 2 inclui ≥ 1 CRITICAL ou HIGH | 3/3 obrigatório | ✅ 11 / 8 / 7 (CRIT+HIGH por projeto) |
| Fase 3 aplicação funciona após refatoração | 3/3 obrigatório | ✅ boot + endpoints validados nos 3 (logs/) |
| Skill completa em `.claude/skills/refactor-arch/` nos 3 projetos | obrigatório | ✅ idêntica nos 3 |
| Relatórios em `reports/` (3 arquivos) | obrigatório | ✅ audit-project-1/2/3.md |
| Catálogo ≥ 8 anti-patterns + deprecated | obrigatório | ✅ 15 APs (incl. AP-14 deprecated com tabela) |
| Playbook ≥ 8 transformações com antes/depois | obrigatório | ✅ 13 padrões (§1–§13) |
| SKILL.md com 3 fases + gate de confirmação | obrigatório | ✅ (gate literal na Fase 2) |
| README com seções A–D | obrigatório | ✅ este documento |
