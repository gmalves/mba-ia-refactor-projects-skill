from flask import Blueprint

from controllers import usuario_controller

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios", methods=["GET"])
def listar():
    return usuario_controller.listar()


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_por_id(usuario_id):
    return usuario_controller.buscar_por_id(usuario_id)


@bp.route("/usuarios", methods=["POST"])
def criar():
    return usuario_controller.criar()


@bp.route("/login", methods=["POST"])
def login():
    return usuario_controller.login()
