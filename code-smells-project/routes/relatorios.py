from flask import Blueprint

from controllers import relatorio_controller

bp = Blueprint("relatorios", __name__)


@bp.route("/relatorios/vendas", methods=["GET"])
def vendas():
    return relatorio_controller.vendas()
