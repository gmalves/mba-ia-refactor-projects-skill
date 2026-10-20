"""Configuração central da aplicação (env-based; nada de segredo hardcoded).

Valores sensíveis vêm de variáveis de ambiente com defaults seguros para
desenvolvimento local. Consulte o arquivo .env.example para a lista completa.
"""
import os
import secrets


def _as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = _as_bool(os.environ.get("FLASK_DEBUG"), default=False)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))

    # Token mínimo para proteger endpoints sensíveis/destrutivos.
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token")

    # SMTP (opcional) — usado pelo serviço de notificação.
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
