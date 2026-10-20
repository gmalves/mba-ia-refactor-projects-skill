from flask import Blueprint

from controllers import category_controller
from middlewares.auth import require_admin

bp = Blueprint("categories", __name__)


@bp.route("/categories", methods=["GET"])
def get_categories():
    return category_controller.get_categories()


@bp.route("/categories", methods=["POST"])
def create_category():
    return category_controller.create_category()


@bp.route("/categories/<int:cat_id>", methods=["PUT"])
def update_category(cat_id):
    return category_controller.update_category(cat_id)


@bp.route("/categories/<int:cat_id>", methods=["DELETE"])
@require_admin
def delete_category(cat_id):
    return category_controller.delete_category(cat_id)
