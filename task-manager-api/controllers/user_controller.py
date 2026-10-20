"""Controladores do domínio de usuários (fluxo request → service → resposta)."""
from flask import jsonify, request

from services import auth_service, user_service


def get_users():
    return jsonify(user_service.list_users()), 200


def get_user(user_id):
    return jsonify(user_service.get_user(user_id)), 200


def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    return jsonify(user_service.create_user(data)), 201


def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    return jsonify(user_service.update_user(user_id, data)), 200


def delete_user(user_id):
    return jsonify(user_service.delete_user(user_id)), 200


def get_user_tasks(user_id):
    return jsonify(user_service.list_user_tasks(user_id)), 200


def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    user = user_service.login(data)
    return jsonify(
        {
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "token": auth_service.generate_token(user),
        }
    ), 200
