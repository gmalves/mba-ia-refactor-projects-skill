"""Controladores do domínio de categorias (fluxo request → service → resposta)."""
from flask import jsonify, request

from services import category_service


def get_categories():
    return jsonify(category_service.list_categories()), 200


def create_category():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    return jsonify(category_service.create_category(data)), 201


def update_category(cat_id):
    data = request.get_json() or {}
    return jsonify(category_service.update_category(cat_id, data)), 200


def delete_category(cat_id):
    return jsonify(category_service.delete_category(cat_id)), 200
