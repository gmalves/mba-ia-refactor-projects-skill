from flask import jsonify, request

from models import pedido_model
from services import notificacao_service, pedido_service
from services.errors import ValidationError

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    try:
        resultado = pedido_service.criar(dados)
    except ValidationError as e:
        return jsonify({"erro": e.mensagem, "sucesso": False}), 400

    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_todos():
    pedidos = pedido_model.get_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_por_usuario(usuario_id):
    pedidos = pedido_model.get_por_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status(pedido_id):
    dados = request.get_json() or {}
    novo_status = dados.get("status", "")

    if novo_status not in STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    pedido = pedido_model.get_por_id(pedido_id)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    status_anterior = pedido["status"]
    pedido_model.atualizar_status(pedido_id, novo_status)

    if novo_status == "aprovado":
        notificacao_service.pedido_aprovado(pedido_id)
    if novo_status == "cancelado" and status_anterior != "cancelado":
        pedido_model.devolver_estoque(pedido_id)
        notificacao_service.pedido_cancelado(pedido_id)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
