from flask import Blueprint

from controllers import produto_controller

bp = Blueprint("produtos", __name__)


@bp.route("/produtos", methods=["GET"])
def listar():
    return produto_controller.listar()


@bp.route("/produtos/busca", methods=["GET"])
def buscar():
    return produto_controller.buscar()


@bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_por_id(produto_id):
    return produto_controller.buscar_por_id(produto_id)


@bp.route("/produtos", methods=["POST"])
def criar():
    return produto_controller.criar()


@bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar(produto_id):
    return produto_controller.atualizar(produto_id)


@bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar(produto_id):
    return produto_controller.deletar(produto_id)
