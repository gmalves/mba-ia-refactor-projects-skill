from flask import Blueprint

from controllers import task_controller
from middlewares.auth import require_admin

bp = Blueprint("tasks", __name__)


@bp.route("/tasks", methods=["GET"])
def get_tasks():
    return task_controller.get_tasks()


@bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    return task_controller.get_task(task_id)


@bp.route("/tasks", methods=["POST"])
def create_task():
    return task_controller.create_task()


@bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    return task_controller.update_task(task_id)


@bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@require_admin
def delete_task(task_id):
    return task_controller.delete_task(task_id)


@bp.route("/tasks/search", methods=["GET"])
def search_tasks():
    return task_controller.search_tasks()


@bp.route("/tasks/stats", methods=["GET"])
def task_stats():
    return task_controller.task_stats()
