import logging

from flask import jsonify, request

from models import usuario_model
from services import usuario_service

logger = logging.getLogger(__name__)


def listar():
    usuarios = usuario_model.get_todos()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar_por_id(usuario_id):
    usuario = usuario_model.get_por_id(usuario_id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    return jsonify({"erro": "Usuário não encontrado"}), 404


def criar():
    nome, email, senha = usuario_service.validar_criacao(request.get_json())
    novo_id = usuario_model.criar(nome, email, senha)
    logger.info("Usuário criado: %s", email)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json() or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    usuario = usuario_model.autenticar(email, senha)
    if usuario:
        logger.info("Login bem-sucedido: %s", email)
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200

    logger.info("Login falhou: %s", email)
    return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
