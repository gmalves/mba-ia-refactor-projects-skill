from flask import Blueprint

from controllers import pedido_controller

bp = Blueprint("pedidos", __name__)


@bp.route("/pedidos", methods=["POST"])
def criar():
    return pedido_controller.criar()


@bp.route("/pedidos", methods=["GET"])
def listar_todos():
    return pedido_controller.listar_todos()


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_por_usuario(usuario_id):
    return pedido_controller.listar_por_usuario(usuario_id)


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status(pedido_id):
    return pedido_controller.atualizar_status(pedido_id)
