from database import get_db

_QUERY_PEDIDOS = """
SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
       i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
FROM pedidos p
LEFT JOIN itens_pedido i ON i.pedido_id = p.id
LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def _agrupar(rows):
    """Agrupa as linhas do JOIN em pedidos com seus itens (uma única query, sem N+1)."""
    pedidos = {}
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            pedidos[pedido_id]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def get_todos():
    db = get_db()
    rows = db.execute(_QUERY_PEDIDOS + " ORDER BY p.id").fetchall()
    return _agrupar(rows)


def get_por_usuario(usuario_id):
    db = get_db()
    rows = db.execute(
        _QUERY_PEDIDOS + " WHERE p.usuario_id = ? ORDER BY p.id", (usuario_id,)
    ).fetchall()
    return _agrupar(rows)


def get_por_id(pedido_id):
    db = get_db()
    return db.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()


def criar(usuario_id, itens):
    """Cria pedido + itens + baixa de estoque em uma única transação atômica."""
    db = get_db()
    total = 0.0
    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', 0)",
            (usuario_id,),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
            total += item["preco_unitario"] * item["quantidade"]

        db.execute("UPDATE pedidos SET total = ? WHERE id = ?", (total, pedido_id))
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()


def devolver_estoque(pedido_id):
    """Devolve ao estoque as quantidades dos itens de um pedido cancelado."""
    db = get_db()
    try:
        itens = db.execute(
            "SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?",
            (pedido_id,),
        ).fetchall()
        for item in itens:
            db.execute(
                "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise


def resumo_vendas():
    db = get_db()
    total_pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    faturamento = db.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
    pendentes = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'").fetchone()[0]
    aprovados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'").fetchone()[0]
    cancelados = db.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'").fetchone()[0]

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": faturamento,
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
    }
