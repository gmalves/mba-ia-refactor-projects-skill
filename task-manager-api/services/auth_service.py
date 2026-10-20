"""Geração de token de autenticação assinado (substitui o antigo token fake)."""
from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def generate_token(user):
    """Retorna um token assinado e expiável contendo id/role do usuário."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user.id, "role": user.role})
