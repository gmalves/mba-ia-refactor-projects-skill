import logging

from flask import jsonify, request

from models import produto_model
from services import produto_service

logger = logging.getLogger(__name__)


def listar():
    produtos = produto_model.get_todos()
    logger.info("Listando %s produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)

    try:
        preco_min = float(request.args["preco_min"]) if request.args.get("preco_min") else None
        preco_max = float(request.args["preco_max"]) if request.args.get("preco_max") else None
    except ValueError:
        return jsonify({"erro": "Preço inválido"}), 400

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def buscar_por_id(produto_id):
    produto = produto_model.get_por_id(produto_id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def criar():
    campos = produto_service.validar_produto(request.get_json(), validar_nome_e_categoria=True)
    novo_id = produto_model.criar(**campos)
    logger.info("Produto criado com ID: %s", novo_id)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(produto_id):
    produto_existente = produto_model.get_por_id(produto_id)
    if not produto_existente:
        return jsonify({"erro": "Produto não encontrado"}), 404

    campos = produto_service.validar_produto(request.get_json(), validar_nome_e_categoria=False)
    produto_model.atualizar(produto_id, **campos)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(produto_id):
    produto = produto_model.get_por_id(produto_id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto_model.deletar(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
