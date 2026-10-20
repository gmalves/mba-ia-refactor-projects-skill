from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


def _to_dict(row):
    # Campo "senha" é intencionalmente omitido (nunca exposto em resposta).
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def _to_dict_login(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_to_dict(row) for row in rows]


def get_por_id(usuario_id):
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return _to_dict(row) if row else None


def criar(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha, method="pbkdf2:sha256"), tipo),
    )
    db.commit()
    return cursor.lastrowid


def autenticar(email, senha):
    """Autentica o usuário e faz upgrade transparente de senhas legadas em texto puro."""
    db = get_db()
    row = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if row is None:
        return None

    if row["senha"] == senha:
        # Senha legada em texto puro: re-hasheia silenciosamente.
        db.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (generate_password_hash(senha, method="pbkdf2:sha256"), row["id"]),
        )
        db.commit()
        return _to_dict_login(row)

    if check_password_hash(row["senha"], senha):
        return _to_dict_login(row)

    return None
