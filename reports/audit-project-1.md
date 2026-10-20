================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 6 | HIGH: 5 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] SQL Injection em todas as queries (AP-01)
File: models.py:28,47-50,57-60,68,92,109-110,126-128,140,148-150,157-160,163-165,174,188,192,220,224,279-280,289-297
Description: Todas as consultas SQL são montadas por concatenação de strings com dados vindos da requisição (`id`, `nome`, `email`, `senha`, `termo`, `categoria`, `preco_min/max`), passadas diretamente a `cursor.execute`.
Impact: Vazamento, alteração e destruição de dados; bypass de login via `' OR '1'='1`; execução de SQL arbitrário através de `/produtos/busca`.
Recommendation: Parametrizar todas as queries com placeholders `?` e tupla de argumentos (Playbook §1).

### [CRITICAL] Credencial hardcoded (AP-02)
File: app.py:7
Description: `SECRET_KEY` fixa no código-fonte (`"minha-chave-super-secreta-123"`), além de `DEBUG=True` em `app.py:8`.
Impact: Segredo exposto no repositório; impossível rotacionar sem alterar código; sessões forjáveis.
Recommendation: Mover para variável de ambiente via módulo de configuração central (Playbook §2).

### [CRITICAL] Endpoints de admin sem autenticação (AP-03)
File: app.py:47-57,59-78
Description: `/admin/reset-db` apaga todas as tabelas e `/admin/query` executa qualquer SQL enviado no body, ambos sem autenticação nem token de admin.
Impact: Qualquer pessoa na rede pode zerar o banco ou executar SQL arbitrário (leitura de senhas, DROP, etc.).
Recommendation: Proteger endpoints administrativos com middleware de auth + token de admin via env, ou removê-los de produção (Playbook §7, §8).

### [CRITICAL] Exposição de dados sensíveis (AP-03)
File: models.py:83,99; controllers.py:287-289
Description: `GET /usuarios` e `GET /usuarios/<id>` devolvem o campo `senha` no JSON; o `/health` expõe `secret_key`, caminho do banco (`db_path`) e flag `debug`.
Impact: Vazamento de senhas (mesmo em texto puro) e de segredos de configuração para qualquer consumidor da API.
Recommendation: Serialização sanitizada sem o campo `senha`; healthcheck sem segredos/configuração interna (Playbook §7, §8).

### [CRITICAL] Senhas em texto puro (AP-04)
File: models.py:109-110,126-128; database.py:76-79
Description: Senhas são armazenadas e comparadas em texto puro (`WHERE email = '...' AND senha = '...'`); seeds criam usuários com `admin123`, `123456`, `senha123`.
Impact: Comprometimento total de todas as contas em caso de vazamento do banco.
Recommendation: Hashing moderno (werkzeug/bcrypt) com salt + migração dos dados existentes (Playbook §3).

### [CRITICAL] God File: models.py concentra banco + negócio + serialização de 4 domínios (AP-05)
File: models.py:1-314
Description: Um único arquivo com acesso a banco, regras de negócio, cálculo de relatório e serialização para produtos, usuários, pedidos e itens, além de `controllers.py` (292 linhas) com validação e regras nos handlers e `app.py` com rotas + admin + acesso a DB inline.
Impact: Impossível testar isoladamente; qualquer mudança impacta vários domínios; alto acoplamento.
Recommendation: Separar em camadas (models/services/controllers/routes/config) por responsabilidade (Playbook §4).

### [HIGH] CRUD e endpoints sensíveis sem autenticação/autorização (AP-06)
File: app.py:11-28
Description: Todos os endpoints de produtos, usuários e pedidos (incluindo POST/PUT/DELETE destrutivos) estão abertos, sem middleware de auth e sem checagem de papéis (`tipo` de usuário nunca é verificado).
Impact: Qualquer um pode criar/alterar/apagar produtos e pedidos, ler usuários e alterar status de pedidos.
Recommendation: Middleware de auth + controle de acesso por papel; token de admin via env quando não há sistema de auth (Playbook §7).

### [HIGH] Regras de negócio em controllers + integrações falsas (AP-07)
File: controllers.py:24-54,87-90,118-121,188-203; controllers.py:208-210,247-250
Description: Validações e regras de negócio vivem nos handlers; "notificações" são `print()` simulados ("ENVIANDO EMAIL/SMS/PUSH", "NOTIFICAÇÃO: ...").
Impact: Regras não reutilizáveis/testáveis; efeitos colaterais escondidos; comportamento falso em produção.
Recommendation: Extrair camada de serviço e validação; substituir prints por serviço de notificação real ou stub explícito (Playbook §9, §4).

### [HIGH] Configuração insegura: debug ativo e bind em 0.0.0.0 (AP-08)
File: app.py:8,88
Description: `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` hardcoded.
Impact: Debugger interativo (RCE potencial) e aplicação exposta em todas as interfaces de rede.
Recommendation: Configurar debug/host/porta via env com defaults seguros; desabilitar debug em produção (Playbook §2, §10).

### [HIGH] Estado global mutável (AP-09)
File: database.py:4-5,9-11
Description: Conexão SQLite global (`db_connection`) compartilhada com `check_same_thread=False` e `db_path` global mutável.
Impact: Bugs de concorrência, estado compartilhado entre requisições, comportamento imprevisível sob múltiplas threads.
Recommendation: Encapsular acesso a dados em classe/serviço com escopo por requisição (Playbook §11).

### [HIGH] Integridade de dados: sem transação e estoque não restaurado (AP-10)
File: models.py:133-169,275-283,65-70
Description: `criar_pedido` faz múltiplos inserts/updates sem transação/rollback; cancelar/alterar status não devolve estoque; `deletar_produto` não remove itens dependentes (órfãos).
Impact: Banco inconsistente em falha parcial; estoque "perdido" ao cancelar; relatórios errados.
Recommendation: Transações atômicas com rollback, cascade/tratamento de dependências e devolução de estoque no cancelamento (Playbook §10).

### [MEDIUM] Queries N+1 em listagem de pedidos (AP-11)
File: models.py:187-199,219-231
Description: Dentro do loop de pedidos há uma query por pedido (itens) e uma query por item (nome do produto), em `get_pedidos_usuario` e `get_todos_pedidos`.
Impact: Performance degrada linearmente com o volume de pedidos; timeouts.
Recommendation: JOIN/agregação em uma única query ou eager loading (Playbook §6).

### [MEDIUM] Validação de entrada ausente ou superficial (AP-12)
File: controllers.py:118-121,188-203,24-54
Description: Valida apenas presença de campos; `float(preco_min)` sem tratamento gera 500; quantidade/`usuario_id` não validam tipo ou valores negativos; categorias e status checados apenas em alguns pontos.
Impact: Dados inválidos no banco, erros 500, estoque negativo e pedidos com quantidades negativas.
Recommendation: Camada única de validação com tipos, intervalos e negativos (Playbook §9).

### [MEDIUM] Duplicação de código e serialização repetida (AP-13)
File: models.py:171-201 vs 203-233; models.py:12-21,31-40,79-87,95-102,304-313; controllers.py (blocos try/except em todos os handlers)
Description: `get_pedidos_usuario` e `get_todos_pedidos` são quase idênticos; o mapeamento linha→dict de produto é repetido 5 vezes; todo handler repete `try/except` + `jsonify({"erro": str(e)}), 500`.
Impact: Correções precisam ser feitas N vezes; divergência de comportamento entre listas.
Recommendation: Extrair serializers, helper de resposta e tratamento central de erro (Playbook §8, §9).

### [LOW] Magic numbers e strings soltas (AP-15)
File: models.py:257-262; controllers.py:47-50,41,85
Description: Limites de desconto (10000/0.1, 5000/0.05, 1000/0.02), tamanhos de nome (2/200) e categoria padrão "geral" espalhados sem constantes.
Impact: Legibilidade e manutenção; regras de negócio difíceis de localizar.
Recommendation: Constantes nomeadas centralizadas (Playbook §12).

### [LOW] Logging improvisado com print() (AP-15)
File: controllers.py:8,11,57,61,106,161,179,182,208-210,219,248,250; app.py:56,83-86
Description: `print()` usado como log em fluxos de negócio e erro, sem nível nem contexto estruturado.
Impact: Sem observabilidade; difícil filtrar e diagnosticar em produção.
Recommendation: Usar o logger do Flask/Python com níveis apropriados (Playbook §13).

### [LOW] Configuração espalhada e hardcoded (AP-15)
File: database.py:5; app.py:88; controllers.py:41,85
Description: Caminho do banco `"loja.db"`, porta 5000 e defaults de categoria/status hardcoded em arquivos distintos.
Impact: Difícil configurar por ambiente; risco de apontar para banco errado.
Recommendation: Módulo de configuração único alimentado por variáveis de ambiente (Playbook §2).

================================
Total: 17 findings
================================

Nenhuma API deprecated encontrada (checklist AP-14 revisado: sem `datetime.utcnow`, `before_first_request`, `flask.ext`, `Model.query.get`, `new Buffer`, `url.parse`, `body-parser` standalone, pacote `request`, `app.del`, `var`, nem callbacks de `fs`).
