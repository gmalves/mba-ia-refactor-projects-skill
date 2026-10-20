from flask import Blueprint

from controllers import admin_controller
from middlewares.auth import require_admin

bp = Blueprint("admin", __name__)


@bp.route("/admin/reset-db", methods=["POST"])
@require_admin
def resetar_banco():
    return admin_controller.resetar_banco()


@bp.route("/admin/query", methods=["POST"])
@require_admin
def executar_query():
    return admin_controller.executar_query()
