from flask import jsonify
from werkzeug.exceptions import HTTPException

from services.errors import ValidationError


def register_error_handlers(app):
    """Registra o tratamento de erro centralizado (remove try/except repetido)."""

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return jsonify({"erro": e.mensagem}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"erro": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unhandled(e):
        app.logger.exception("Erro interno não tratado")
        return jsonify({"erro": "Erro interno"}), 500
