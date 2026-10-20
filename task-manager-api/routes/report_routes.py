from flask import Blueprint

from controllers import report_controller

bp = Blueprint("reports", __name__)


@bp.route("/reports/summary", methods=["GET"])
def summary_report():
    return report_controller.summary_report()


@bp.route("/reports/user/<int:user_id>", methods=["GET"])
def user_report(user_id):
    return report_controller.user_report(user_id)
