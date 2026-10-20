import os
import secrets


class Config:
    """Configuração central da aplicação.

    Valores sensíveis NUNCA são hardcoded: vêm de variáveis de ambiente com
    defaults seguros para desenvolvimento local (ver .env.example).
    """

    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token")
    AMBIENTE = os.environ.get("AMBIENTE", "producao")
    VERSAO = "1.0.0"
