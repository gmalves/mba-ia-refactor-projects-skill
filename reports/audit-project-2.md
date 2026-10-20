================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express (^4.18.2)
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] Credenciais e segredos hardcoded
File: src/utils.js:1-7
Description: O objeto `config` contém credenciais de produção em texto puro: `dbPass` ("senha_super_secreta_prod_123"), `paymentGatewayKey` ("pk_live_1234567890abcdef") e `dbUser`.
Impact: Segredos expostos no repositório; vazamento de credenciais; rotação exige alterar código e redeploy.
Recommendation: Mover para variáveis de ambiente em um módulo de config central (playbook §2).

### [CRITICAL] Exposição de dados sensíveis em logs
File: src/AppManager.js:45
Description: `console.log` imprime o número completo do cartão (`cc`) e a chave do gateway de pagamento (`config.paymentGatewayKey`) a cada checkout.
Impact: Vazamento de dados de cartão (PCI) e da chave de produção em logs; não-conformidade PCI-DSS.
Recommendation: Remover dados sensíveis do log; logar apenas IDs/status (playbook §7).

### [CRITICAL] Armazenamento de senha inseguro (hash caseiro, sem salt)
File: src/utils.js:17-23; src/AppManager.js:18,68
Description: `badCrypto` é um "hash" caseiro (loop de base64 truncado em 10 chars) sem salt; a senha seed é armazenada em texto puro ("123") e o checkout usa senha default "123456".
Impact: Comprometimento total das contas em caso de vazamento do banco; hash previsível.
Recommendation: Usar hashing moderno (bcrypt/scrypt) com salt; migrar dados existentes (playbook §3).

### [CRITICAL] God Class — AppManager concentra banco + negócio + rotas + relatórios
File: src/AppManager.js:4-139
Description: A classe `AppManager` inicializa o banco (DDL + seeds), registra rotas, implementa as regras de checkout e monta relatórios — tudo no mesmo arquivo/objeto.
Impact: Impossível testar em isolamento; qualquer mudança afeta tudo; viola SRP e MVC.
Recommendation: Separar em camadas: config/, models/, services/, controllers/, routes/ (playbook §4).

### [CRITICAL] Autenticação/autorização ausente em endpoints sensíveis
File: src/AppManager.js:80,131
Description: O relatório administrativo (`/api/admin/financial-report`) e a exclusão de usuários (`DELETE /api/users/:id`) não têm nenhum middleware de auth; qualquer cliente pode acessá-los.
Impact: Qualquer um pode ler dados financeiros e apagar usuários; escalada de privilégio.
Recommendation: Middleware de auth + token de admin via env (playbook §7).

### [HIGH] Regras de negócio dentro das rotas + integração de pagamento falsa
File: src/AppManager.js:28-78
Description: Toda a lógica do checkout (validação, decisão de pagamento `cc.startsWith("4")`, criação de usuário, matrícula, pagamento, auditoria) está embutida no handler da rota, em callbacks aninhados.
Impact: Baixa coesão, regra impossível de reutilizar/testar; efeitos colaterais escondidos.
Recommendation: Extrair services (checkout/pagamento) e camada de validação; handler só orquestra (playbook §4, §9).

### [HIGH] Estado global mutável
File: src/utils.js:9-10
Description: `globalCache` e `totalRevenue` são globais de módulo usados como cache/contador compartilhado; `totalRevenue` é exportado mas nunca usado (dead code).
Impact: Bugs de concorrência, estado compartilhado imprevisível, crescimento sem limite.
Recommendation: Encapsular em classe/serviço com escopo controlado; remover dead code (playbook §11).

### [HIGH] Integridade de dados: exclusão sem cascade e sem transação
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` remove o usuário mas deixa matrículas e pagamentos órfãos (o próprio código admite "ficaram sujos no banco"); não há transação nem cascade.
Impact: Banco inconsistente; relatórios financeiros errados.
Recommendation: Transações atômicas + cascades (FOREIGN KEY / ON DELETE) ou deleção em etapas (playbook §10).

### [MEDIUM] Queries N+1 no relatório financeiro
File: src/AppManager.js:89-127
Description: Para cada curso, consulta matrículas; para cada matrícula, consulta usuário e pagamento em callbacks aninhados (3 níveis de loop + query).
Impact: Performance degrada linearmente com o volume; timeouts.
Recommendation: JOIN/agregação em poucas queries (playbook §6).

### [MEDIUM] Validação de entrada superficial
File: src/AppManager.js:35
Description: O checkout valida apenas a presença de `usr/eml/c_id/card`; não valida tipos, formato de e-mail, cartão ou valor do `c_id`; a senha (`pwd`) nem é exigida.
Impact: Dados inválidos no banco, erros de tipo e lógica de negócio furada.
Recommendation: Camada única de validação (presença + tipo + formato) (playbook §9).

### [LOW] Magic strings, nomenclatura críptica e logging improvisado
File: src/AppManager.js:29-33,46; src/utils.js:12-15
Description: Nomes crípticos (`u`, `e`, `p`, `cid`, `cc`); string mágica `"4"` para decidir pagamento; `console.log` usado como logging de negócio.
Impact: Legibilidade e manutenção ruins; decisões obscuras.
Recommendation: Nomes descritivos, constantes nomeadas, logging adequado (playbook §12/§13).

Nenhuma SQL Injection encontrada (queries já parametrizadas com `?`).
Nenhuma API deprecated encontrada (usa `Buffer.from`, `express.json`, `app.delete`, `const`/`let`).

================================
Total: 11 findings
================================
