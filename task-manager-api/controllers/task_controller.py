"""Controladores do domínio de tasks (fluxo request → service → resposta)."""
from flask import jsonify, request

from services import task_service


def get_tasks():
    return jsonify(task_service.list_tasks()), 200


def get_task(task_id):
    return jsonify(task_service.get_task(task_id)), 200


def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    return jsonify(task_service.create_task(data)), 201


def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    return jsonify(task_service.update_task(task_id, data)), 200


def delete_task(task_id):
    return jsonify(task_service.delete_task(task_id)), 200


def search_tasks():
    return jsonify(
        task_service.search_tasks(
            query=request.args.get("q", ""),
            status=request.args.get("status", ""),
            priority=request.args.get("priority", ""),
            user_id=request.args.get("user_id", ""),
        )
    ), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
