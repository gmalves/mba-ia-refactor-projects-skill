import secrets
from functools import wraps

from flask import current_app, jsonify, request


def require_admin(f):
    """Exige o header X-Admin-Token igual ao ADMIN_TOKEN configurado."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token", "")
        if not token or not secrets.compare_digest(token, current_app.config["ADMIN_TOKEN"]):
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)

    return wrapper
