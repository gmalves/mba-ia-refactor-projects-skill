================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0)
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 4 | LOW: 1

## Findings

### [CRITICAL] Credenciais e segredos hardcoded
File: app.py:13; services/notification_service.py:7-10
Description: `SECRET_KEY = 'super-secret-key-123'` fixa no código; credenciais SMTP (`smtp.gmail.com`, `taskmanager@gmail.com`, `senha123`) literais no serviço de notificação; URI do banco `sqlite:///tasks.db` hardcoded em app.py:11.
Impact: Segredo e credenciais expostos em repositório; rotação impossível sem alterar código; credencial de e-mail vazada.
Recommendation: Mover para variáveis de ambiente em um módulo `config/settings.py` com defaults seguros (playbook §2).

### [CRITICAL] Exposição de dados sensíveis (hash de senha nas respostas)
File: models/user.py:21; routes/user_routes.py:33,85,129,209
Description: `User.to_dict()` inclui o campo `'password'`; como consequência o hash da senha vaza em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login`.
Impact: Vazamento do hash (mesmo MD5) permite ataque offline e facilita sequestro de contas.
Recommendation: Remover `password` de `to_dict()` e criar serialização sanitizada (playbook §8).

### [CRITICAL] Armazenamento de senha inseguro (MD5 sem salt)
File: models/user.py:29,32
Description: Senhas hasheadas com `hashlib.md5(pwd.encode()).hexdigest()`, sem salt e comparadas via `==`; senhas de seed em texto puro (`seed.py:19,26,33`).
Impact: MD5 é quebrável por rainbow tables/GPU; comprometimento total das contas em caso de vazamento do banco.
Recommendation: Usar `werkzeug.security.generate_password_hash/check_password_hash` (pbkdf2/scrypt com salt) + migração transparente dos hashes legados no login (playbook §3).

### [CRITICAL] Autenticação/autorização ausente e token falso
File: routes/user_routes.py:210; rotas CRUD de tasks/users/categories (task_routes.py:65,85,156,225; user_routes.py:42,92,134; report_routes.py:167,190,211)
Description: Nenhum middleware de auth em nenhum endpoint; login devolve `'fake-jwt-token-' + str(user.id)` (token previsível, sem verificação); `role`/`is_admin` definidos mas nunca checados; `DELETE /users/<id>` e demais CRUD abertos.
Impact: Qualquer pessoa pode ler, criar, alterar e apagar dados; escalada de privilégio trivial.
Recommendation: Middleware de auth e proteção mínima via token de admin por env para endpoints sensíveis (playbook §7).

### [HIGH] Regras de negócio em rotas + serviço/integração mortos
File: routes/task_routes.py:13-299; routes/report_routes.py:12-223; services/notification_service.py:1-48
Description: Validação, serialização, cálculo de "overdue" e agregação de relatórios embutidos nos handlers; `report_routes.py` mistura relatórios e CRUD de categorias (domínios distintos). `NotificationService` e todo o módulo `utils/helpers.py` (116 linhas) nunca são importados/usados em lugar nenhum — dead code.
Impact: Baixa coesão e reutilização; comportamento duplicado; código morto que engana a manutenção (notificação nunca é enviada).
Recommendation: Extrair controllers (fluxo) e services (regras/validação); remover ou conectar o serviço de notificação (playbook §4, §9).

### [HIGH] Configuração insegura / modo debug em produção
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` hardcoded; debug ativo expõe o debugger interativo em todas as interfaces.
Impact: Debugger interativo permite execução remota de código (RCE) em produção.
Recommendation: Config via env (`FLASK_DEBUG` default false) e bind em `127.0.0.1` por padrão (playbook §2).

### [HIGH] Integridade de dados: exclusão de categoria deixa tasks órfãs
File: routes/report_routes.py:211-223; models/task.py:14; models/category.py:20
Description: `DELETE /categories/<id>` remove a categoria sem tratar as tasks que a referenciam; a FK `category_id` não tem `ON DELETE` e o relacionamento não configura cascade, deixando tasks apontando para categoria inexistente.
Impact: Banco inconsistente; relatórios/consultas retornam `category_name: null` inesperado ou quebram.
Recommendation: Cascata explícita ou transação que desassocia/re-atribui as tasks antes da exclusão (playbook §10).

### [MEDIUM] Queries N+1 (consulta dentro de laço)
File: routes/task_routes.py:42-57; routes/report_routes.py:55-61,162-163
Description: `get_tasks` faz `User.query.get(...)` e `Category.query.get(...)` por task; `summary_report` faz `Task.query.filter_by(user_id=...)` por usuário; `get_categories` faz `Task.query.filter_by(category_id=...)` por categoria.
Impact: Performance degrada linearmente com o volume de registros; timeouts em bases maiores.
Recommendation: Eager loading (`db.joinedload`) ou agregações `GROUP BY`/`COUNT` (playbook §6).

### [MEDIUM] Validação de entrada ausente ou superficial
File: routes/task_routes.py:113-114,136-138,261,264; routes/user_routes.py:124-125
Description: `priority` é comparado sem conversão de tipo (string causa `TypeError` → 500); `int(priority)`/`int(user_id)` em `/tasks/search` sem try/except; `due_date` só aceita `%Y-%m-%d` em um ponto e `%d/%m/%Y` em outro (inconsistente); `active` não validado como booleano.
Impact: Dados inválidos no banco, erros 500, lógica de negócio furada.
Recommendation: Camada única de validação (tipos/intervalos/formato) reutilizada por todos os handlers, erros 400 padronizados (playbook §9).

### [MEDIUM] Duplicação de código / serialização repetida
File: routes/task_routes.py:16-39,30-39,71-80,282-287; routes/user_routes.py:161-180; routes/report_routes.py:33-43,132-135; models/task.py:23-36
Description: Mapeamento task→dict replicado em 3 lugares; cálculo de "overdue" duplicado em 6 pontos; lista de status válidos copiada em 4 arquivos; `try/except` idêntico em todos os handlers mutáveis.
Impact: Correções precisam ser feitas N vezes; risco de divergência de comportamento entre endpoints.
Recommendation: Extrair serializers, constantes (`VALID_STATUSES`) e helpers de domínio únicos (playbook §8, §9).

### [MEDIUM] APIs deprecated (datetime.utcnow, Model.query.get)
File: models/category.py:11; models/task.py:15-16; models/user.py:14; utils/helpers.py:38; task_routes.py:31,72,285; user_routes.py:172; report_routes.py:35,42,45,133; e `Model.query.get(...)` em task_routes.py:67,117,122,158,187,195,227; user_routes.py:29,94,136,155; report_routes.py:105,192,213
Description: `datetime.utcnow()` (deprecated no Python 3.12+) gera datetimes naive; `Model.query.get(id)` é o acesso legado do SQLAlchemy 2.0.
Impact: Warnings e remoção futura; comportamento inconsistente de fuso horário.
Recommendation: `datetime.now(timezone.utc)` e `db.session.get(Model, id)` (playbook §12).

### [LOW] Magic numbers/strings, logging improvisado e dead code
File: task_routes.py:7,62,141,149,153,210,219,234,236; user_routes.py:83,89,130,147,149; report_routes.py:8,186,207,221; app.py:7; utils/helpers.py:1-116
Description: `print()` como logging; `except:` nu (sem tipo) em vários handlers; `type(x) == list` em vez de `isinstance`; imports não usados (`os, sys, json` em app.py/task_routes.py); módulo `utils/helpers.py` inteiro é código morto (funções e constantes nunca usadas).
Impact: Legibilidade e manutenção; bugs silenciosos por `except:` nu que mascara erros reais.
Recommendation: Usar `logging`, `except Exception as e:` com log, `isinstance`, remover imports/funções mortas (playbook §12/§13).

================================
Total: 12 findings
================================
