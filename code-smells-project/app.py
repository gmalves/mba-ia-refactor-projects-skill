import logging

from flask import Flask
from flask_cors import CORS

from config.settings import Config
from database import close_db
from middlewares.error_handler import register_error_handlers
from routes import register_blueprints
from schema import inicializar_banco

logging.basicConfig(level=logging.INFO)


def create_app():
    """Application factory: cria e configura a aplicação (composition root)."""
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    inicializar_banco(app.config["DB_PATH"])

    register_error_handlers(app)
    register_blueprints(app)
    app.teardown_appcontext(close_db)

    return app


app = create_app()


if __name__ == "__main__":
    app.logger.info("SERVIDOR INICIADO")
    app.logger.info("Rodando em http://%s:%s", app.config["HOST"], app.config["PORT"])
    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
