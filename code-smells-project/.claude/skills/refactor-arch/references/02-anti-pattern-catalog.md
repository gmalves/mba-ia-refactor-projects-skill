# Referência 02 — Catálogo de Anti-Patterns (Fase 2)

Escala de severidade padronizada (use SEMPRE esta):

- **CRITICAL:** falhas graves de arquitetura/segurança que impedem funcionamento correto, expõem dados sensíveis (credenciais hardcoded, SQL injection) ou violam completamente a separação de responsabilidades (ex.: God Class com banco + lógica + rotas no mesmo arquivo).
- **HIGH:** fortes violações de MVC/SOLID que dificultam muito manutenção e testes (ex.: negócio pesado dentro de controllers, estado global mutável, sem camada de serviço).
- **MEDIUM:** padronização, duplicação, gargalos moderados (ex.: N+1, validações ausentes, uso inadequado de middlewares).
- **LOW:** legibilidade, nomenclatura ruim, magic numbers.

Para cada finding do relatório: severidade, título, arquivo:linha exatos, descrição, impacto e recomendação.

---

## AP-01 [CRITICAL] SQL Injection (queries concatenadas)

**Sinais de detecção:** strings SQL montadas com `+`, `%`, f-string, ou template literal contendo variáveis (`"SELECT * FROM x WHERE id = " + str(id)`, `` `SELECT * FROM users WHERE email = '${email}'` ``) passadas para `cursor.execute`, `db.run`, `db.all`, `db.get`, `text()`. Também: filtros de busca que interpolam o termo do usuário.
**Impacto:** vazamento de dados, bypass de autenticação (`' OR '1'='1`), destruição de dados.
**Correção:** parâmetros posicionais (`?`, `%s`) — ver Playbook §1.

## AP-02 [CRITICAL] Credenciais/segredos hardcoded

**Sinais:** literais atribuídos a `SECRET_KEY`, `password`, `pass`, `apiKey`, `api_key`, `token`, `paymentGatewayKey`, `dbPass`, `email_password`; valores como `"minha-chave-super-secreta-123"`, `"pk_live_..."`; credenciais em `config` no código.
**Impacto:** vazamento de credenciais em repositório público; rotação impossível sem alterar código.
**Correção:** mover para variáveis de ambiente + módulo de config — ver Playbook §2.

## AP-03 [CRITICAL] Exposição de dados sensíveis

**Sinais:** campos `password`/`senha` (mesmo hasheados) em respostas de API (`to_dict()` incluindo senha); endpoints de admin/banco sem autenticação (ex.: `/admin/query` executando SQL arbitrário, `/admin/reset-db`, `/api/admin/*`); logs de números de cartão + chaves; healthcheck devolvendo caminho do banco, debug e segredos.
**Impacto:** sequestro de contas, PCI/privacidade, execução arbitrária de SQL.
**Correção:** serialização sanitizada, endpoints sensíveis protegidos por auth/token de admin — Playbook §7, §8.

## AP-04 [CRITICAL] Armazenamento de senha inseguro (plaintext/MD5/“hash” caseiro)

**Sinais:** comparação direta de senha em SQL (`WHERE senha = '...'`); `hashlib.md5`/`sha1` para senha; função própria de “hash” (ex.: loop de `base64`); ausência de salt; senhas seed em texto puro.
**Impacto:** comprometimento total de contas em caso de vazamento do banco.
**Correção:** hashing moderno (werkzeug/bcrypt) + migração de dados existentes — Playbook §3.

## AP-05 [CRITICAL] God Class / God File / God Method

**Sinais:** um arquivo/classe concentra banco + negócio + rotas + relatórios para vários domínios; arquivo com centenas de linhas e funções de áreas distintas; “Manager” que inicializa DB, registra rotas e implementa regras (ex.: `AppManager.js`).
**Impacto:** impossível testar em isolamento; qualquer mudança afeta tudo.
**Correção:** separar em camadas por responsabilidade — Playbook §4.

## AP-06 [CRITICAL/HIGH] Autenticação/autorização ausente em endpoints sensíveis

**Sinais:** CRUD e endpoints de admin sem nenhum middleware de auth; “tokens” falsos (`'fake-jwt-token-' + id`); papéis/roles definidos mas nunca checados; endpoints destrutivos abertos (`DELETE /users/:id`).
**Impacto:** qualquer um pode ler/alterar/apagar dados; escalada de privilégio.
**Correção:** middleware de auth + token de admin via env (quando não há sistema de auth) — Playbook §7.

## AP-07 [HIGH] Regras de negócio em controllers/rotas + integrações falsas

**Sinais:** validações + cálculo de negócio + serialização dentro dos handlers; notificações simuladas com `print("ENVIANDO EMAIL...")`; serviços existentes mas nunca chamados; serviços/instâncias mortos (dead code).
**Impacto:** baixa coesão, impossível reutilizar/testar regra; efeitos colaterais escondidos.
**Correção:** extrair serviços e camada de validação — Playbook §9, §4.

## AP-08 [HIGH] Configuração insegura / modo debug em produção

**Sinais:** `debug=True`, `app.run(..., host='0.0.0.0')`, DEBUG hardcoded, `app.config['DEBUG'] = True`.
**Impacto:** debugger interativo (RCE), exposição em todas as interfaces.
**Correção:** configuração via env com defaults seguros — Playbook §2, §10.

## AP-09 [HIGH] Estado global mutável

**Sinais:** variáveis globais de módulo usadas como cache/contadores (`globalCache`, `totalRevenue`), conexão de banco global compartilhada (`global db_connection` com `check_same_thread=False`), listas globais crescendo sem limite.
**Impacto:** bugs de concorrência, memory leak, comportamento imprevisível.
**Correção:** encapsular em classes/serviços com escopo controlado — Playbook §11.

## AP-10 [HIGH] Integridade de dados: exclusões sem cascade e sem transação

**Sinais:** `DELETE` que deixa órfãos (matrículas/pagamentos “sujos”, comentário admitindo); ausência de `rollback`/transação em operações multi-passo; `criar_pedido` sem restore de estoque ao cancelar; quantidade negativa aceita.
**Impacto:** banco inconsistente; relatórios errados; fraude (estoque/preço).
**Correção:** transações atômicas + cascades + validações de fluxo — Playbook §10.

## AP-11 [MEDIUM] Queries N+1 (consulta dentro de laço)

**Sinais:** query dentro de `for`/`forEach` por linha (uma consulta por item para buscar nome/relacionados); loops que chamam `User.query.get(...)` por task; callbacks aninhados que consultam por enrollment/item; contagem por categoria em loop.
**Impacto:** performance degrada linearmente com o volume; timeouts.
**Correção:** JOIN/agregação/eager loading — Playbook §6.

## AP-12 [MEDIUM] Validação de entrada ausente ou superficial

**Sinais:** valida apenas presença de campos; não valida tipo/intervalo/negativo (quantidade negativa em pedido); `int()`/`float()` sem tratamento; data sem formato checado em todos os pontos; e-mail simples regex duplicado sem camada.
**Impacto:** dados inválidos no banco, erros 500, lógica de negócio furada.
**Correção:** camada única de validação — Playbook §9.

## AP-13 [MEDIUM] Duplicação de código / serialização repetida

**Sinais:** o mesmo mapeamento objeto→dict repetido em 2-3 lugares; mesma lista de constantes copiada (status válidos); blocos `try/except` idênticos em dezenas de handlers; lógicas quase idênticas (`get_pedidos_usuario` vs `get_todos_pedidos`).
**Impacto:** correções precisam ser feitas N vezes; divergência de comportamento.
**Correção:** extrair serializers/constantes/utilitários — Playbook §8, §9.

## AP-14 [MEDIUM] APIs deprecated / constructs obsoletos

**Sinais de detecção (checklist obrigatório):**

| API obsoleta | Onde | Equivalente moderno |
|---|---|---|
| `datetime.utcnow()` (deprecated no Python 3.12+) | Python | `datetime.now(timezone.utc)` |
| `Model.query.get(id)` (legacy SQLAlchemy 2.0) | Flask-SQLAlchemy | `db.session.get(Model, id)` |
| `@app.before_first_request` (removido no Flask 2.3) | Flask | setup dentro do application factory |
| `flask.ext.*` (removido) | Flask | import direto do pacote |
| `new Buffer(...)` | Node.js | `Buffer.from(...)` |
| `url.parse()` / `url.resolve()` | Node.js | `new URL()` |
| `body-parser` (standalone) | Express | `express.json()` |
| pacote `request` (deprecated) | Node.js | `fetch` nativo / `axios` |
| `app.del()` | Express | `app.delete()` |
| `var` | JS | `const`/`let` |
| callbacks de `fs` em vez de promises | Node.js | `fs/promises` |

**Impacto:** warnings, remoções futuras, comportamento inconsistente (datas naive). **Correção:** substituições da tabela — Playbook §12.

## AP-15 [LOW] Magic numbers/strings, nomenclatura e logging improvisado

**Sinais:** limites numéricos soltos (10000/5000/1000, 0.1/0.05, portas, `len < 2`), strings de status repetidas sem constantes, `print()` como logging em fluxos de erro/negócio, nomes crípticos (`u`, `e`, `p`, `cc`), imports não usados, `except:` nu sem tipo, `type(x) == list` em vez de `isinstance`.
**Impacto:** legibilidade e manutenção; bugs silenciosos (except nu).
**Correção:** constantes nomeadas, logging adequado, limpeza — Playbook §12/§13.

---

## Regras de classificação (resumo rápido)

- Exposição/destruição de dados, auth bypass, execução arbitrária → **CRITICAL**.
- Violação estrutural séria (God files, sem camadas, estado global, integração falsa) → **HIGH**.
- Performance/duplicação/validação → **MEDIUM**.
- Legibilidade/nomenclatura/magic numbers → **LOW**.

Achado que não se encaixe em nenhum AP: classifique pela escala acima e registre com título descritivo.
