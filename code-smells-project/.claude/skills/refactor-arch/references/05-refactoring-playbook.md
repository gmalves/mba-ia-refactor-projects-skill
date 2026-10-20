# Referência 05 — Playbook de Refatoração (Fase 3)

Transformações concretas, anti-pattern por anti-pattern, com exemplos **antes/depois**. Aplique o padrão correspondente a cada finding do relatório.

---

## §1. SQL Injection → queries parametrizadas (AP-01)

**Antes (Python/sqlite3):**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```

**Depois:**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```
**Antes (Node/sqlite3):**
```js
this.db.get(`SELECT * FROM courses WHERE id = ${cid}`, cb);
```
**Depois:**
```js
this.db.get("SELECT * FROM courses WHERE id = ?", [cid], cb);
```
Regra: **nenhuma variável entra em string SQL** — sempre placeholders (`?` / `%s` / bind do ORM). Valores numéricos também são parametrizados.

---

## §2. Segredos hardcoded → config + variáveis de ambiente (AP-02, AP-08)

**Antes:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.run(host="0.0.0.0", port=5000, debug=True)
```
**Depois:**
```python
# config/settings.py
import os, secrets
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    PORT = int(os.environ.get("PORT", "5000"))
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
```
```python
# app.py (entry)
app.config.from_object(Config)
app.run(host="127.0.0.1", port=app.config["PORT"], debug=app.config["DEBUG"])
```
Node:
```js
// config/settings.js
module.exports = {
  port: Number(process.env.PORT || 3000),
  adminToken: process.env.ADMIN_TOKEN || "change-me", // NUNCA logar
  dbPass: process.env.DB_PASS,
};
```
Sempre crie/atualize `.env.example` (sem valores reais) e garanta `.env` no `.gitignore`.

---

## §3. Senhas plaintext/MD5 → hashing moderno com migração (AP-04)

**Antes:**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
# e login comparando senha em texto: WHERE senha = '...'
```
**Depois (Flask):**
```python
from werkzeug.security import generate_password_hash, check_password_hash
hash_ = generate_password_hash(password)          # pbkdf2/scrypt com salt
check_password_hash(self.password, pwd)
```
**Migração transparente de dados existentes:** no primeiro acesso/login, detecte hash legado (padrão `^[a-f0-9]{32}$` → md5; ou texto puro) e re-hasheie:
```python
def verify_and_upgrade(self, pwd):
    if self.password == pwd or self.password == hashlib.md5(pwd.encode()).hexdigest():
        self.password = generate_password_hash(pwd)   # upgrade silencioso
        db.session.commit()
        return True
    return check_password_hash(self.password, pwd)
```
Node: `crypto.scrypt` / `bcryptjs` com salt e comparação em tempo constante.

---

## §4. God File/Class → separação por camadas (AP-05)

**Antes:** `models.py` (350 linhas) contém queries + regras + relatórios de 4 domínios; `AppManager.js` inicializa banco, define rotas e implementa negócio.

**Depois (mapa de decomposição):**
```
arquivo_unico.py
├── config/settings.py         ← constantes/segredos
├── database.py                ← conexão (sem DDL/seeds espalhados)
├── models/<dominio>_model.py  ← queries parametrizadas por domínio
├── services/<dominio>_service.py ← regras (totais, descontos, estoque)
├── controllers/<dominio>_controller.py ← fluxo request→resposta
├── views/routes.py            ← só rotas
└── app.py                     ← composition root
```
Método prático: liste todas as funções do arquivo original; para cada uma pergunte "isto é dado, regra, fluxo ou rota?"; mova para a camada correspondente; atualize imports.

---

## §5. Tratamento de erro repetido → erro centralizado (AP-13)

**Antes (todo handler):**
```python
def listar_produtos():
    try:
        ...
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
```
**Depois:**
```python
# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle_error(e):
    if isinstance(e, HTTPException):
        return jsonify({"erro": e.description}), e.code
    app.logger.exception("Erro interno")   # loga sem vazar stack ao cliente
    return jsonify({"erro": "Erro interno"}), 500
```
Handlers deixam de repetir try/except (mantenha apenas onde houver tratamento específico). Não vaze `str(e)`/stacktrace ao cliente. Express: middleware `(err, req, res, next)` registrado por último.

---

## §6. N+1 → JOIN / eager loading / agregação (AP-11)

**Antes:**
```python
for row in rows:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
**Depois:**
```python
cursor.execute("""
    SELECT p.numero, i.produto_id, pr.nome, i.quantidade, i.preco_unitario
    FROM pedidos p
    JOIN itens_pedido i ON i.pedido_id = p.id
    JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.id = ?
""", (pedido_id,))
```
ORM (Flask-SQLAlchemy): `Task.query.options(db.joinedload(Task.user), db.joinedload(Task.category))`; Node: `Promise.all` de queries preparadas ou JOIN único. Contagens por grupo: `GROUP BY` com `COUNT`.

---

## §7. Endpoints sensíveis → proteção mínima via token de admin (AP-03, AP-06)

**Antes:** `POST /admin/query` executa qualquer SQL, sem auth.
**Depois (preserve o endpoint, mas seguro):**
```python
# middlewares/auth.py
def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        if not token or token != current_app.config["ADMIN_TOKEN"]:
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return wrapper
```
- `/admin/query`: exige token e aceita **apenas SELECT** (rejeite DDL/DML com 400/403).
- `/admin/reset-db`: exige token.
- `ADMIN_TOKEN` vem do ambiente; documente no `.env.example`.
- Se não houver sistema de auth completo, o token de admin é a proteção mínima aceitável; NUNCA deixe o endpoint aberto.

---

## §8. Serialização sanitizada (AP-03)

**Antes:** `to_dict()` devolve `'password': self.password` / `"senha": row["senha"]`.
**Depois:** remova campos sensíveis do payload; crie serializers explícitos por entidade:
```python
def to_dict(self):
    return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}
```
Regra: senha (hash ou não) NUNCA aparece em resposta de API, logger ou healthcheck.

---

## §9. Validação central + regras no service (AP-07, AP-12)

**Antes:** controller valida só presença; quantidade negativa passa e corrompe estoque/total.
**Depois:**
```python
# services/pedido_service.py
class ValidationError(Exception): ...
class PedidoService:
    @staticmethod
    def criar(usuario_id, itens):
        if not itens:
            raise ValidationError("Pedido deve ter ao menos 1 item")
        for item in itens:
            qtd = int(item.get("quantidade", 0))
            if qtd <= 0:
                raise ValidationError("Quantidade deve ser positiva")
        # ... cálculo do total, checagem de estoque, transação única
```
Validações de formato (email, data, status, prioridade) em um único módulo de validação reutilizado por todos os handlers; erros de validação retornam 400 padronizado.

---

## §10. Transações e integridade referencial (AP-10)

**Antes:** delete de usuário deixa matrículas/pagamentos órfãos; pedido cancelado não devolve estoque; operações multi-passo sem rollback.
**Depois:**
- Exclusões em cascata: `FOREIGN KEY ... ON DELETE CASCADE` **ou** deleção explícita dos dependentes em uma transação única.
- Operações multi-passo em uma transação (commit único + `rollback` no erro).
- Fluxos de negócio completos: cancelar pedido → devolver estoque no mesmo serviço/transação.
```python
try:
    cursor.execute("DELETE FROM itens_pedido WHERE pedido_id = ?", (id,))
    cursor.execute("DELETE FROM pedidos WHERE id = ?", (id,))
    db.commit()
except Exception:
    db.rollback()
    raise
```

---

## §11. Estado global mutável → encapsulamento (AP-09)

**Antes:** `global db_connection`, `globalCache`, `totalRevenue` de módulo.
**Depois:**
- Conexão: módulo `database` com factory/getter controlado (`get_db()` por request ou pool) — sem `global` exposto nem `check_same_thread=False` gratuito.
- Cache: classe `CacheService` com escopo explícito e limite (ou remova se não usado).
- Contadores: calcule a partir do banco (fonte de verdade) em vez de manter em memória.

---

## §12. APIs deprecated → equivalentes modernos (AP-14)

| Antes | Depois |
|---|---|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` (import `timezone`) — datetimes aware |
| `Model.query.get(id)` | `db.session.get(Model, id)` |
| `@app.before_first_request` | setup no `create_app()` |
| `new Buffer(x)` | `Buffer.from(x)` |
| `url.parse(s)` | `new URL(s)` |
| `body-parser` | `express.json()` |
| callbacks `fs` | `fs/promises` com async/await |
| `var` | `const`/`let` |

Aplique com cuidado: mantenha compatibilidade (ex.: `str(datetime)` continua funcionando; serialize datas com ISO). Faça a substituição em TODAS as ocorrências listadas no relatório.

---

## §13. Limpeza final (AP-15)

- Magic numbers → constantes nomeadas (`DESCONTO_FAIXA_ALTA = 10000`, `MAX_TITLE_LENGTH = 200`).
- `print()` → `logging` (níveis adequados; sem dados sensíveis).
- Remover imports/funções/instâncias mortas encontradas na auditoria.
- `except:` nu → `except Exception as e:` com log.
- `type(x) == list` → `isinstance(x, list)`.
- Nomenclatura: `u`, `e`, `cc` → `usuario`, `email`, `numero_cartao`.

---

## Ordem de aplicação sugerida na Fase 3

1. Config/segredos (§2) e estrutura de diretórios (§4) — base para tudo.
2. Segurança crítica: SQLi (§1), senhas (§3), endpoints sensíveis (§7), sanitização (§8).
3. Fluxo: controllers/services (§4, §9), erro central (§5), transações (§10).
4. Performance: N+1 (§6).
5. Modernização: deprecated (§12).
6. Limpeza: §13.
