from flask import Blueprint

from controllers import geral_controller

bp = Blueprint("geral", __name__)


@bp.route("/")
def index():
    return geral_controller.index()


@bp.route("/health")
def health():
    return geral_controller.health()
