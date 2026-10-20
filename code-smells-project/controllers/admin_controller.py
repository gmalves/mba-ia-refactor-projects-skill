from flask import jsonify, request

from database import get_db


def resetar_banco():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    dados = request.get_json() or {}
    query = dados.get("sql", "")

    if not query:
        return jsonify({"erro": "Query não informada"}), 400
    if not query.strip().upper().startswith("SELECT"):
        return jsonify({"erro": "Apenas consultas SELECT são permitidas"}), 403

    db = get_db()
    try:
        rows = db.execute(query).fetchall()
        result = [dict(row) for row in rows]
        return jsonify({"dados": result, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
