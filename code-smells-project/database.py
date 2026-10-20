import sqlite3

from flask import current_app, g


def get_db():
    """Retorna a conexão SQLite da requisição atual (escopo por request).

    A conexão é criada sob demanda e fechada ao final da requisição via
    teardown_appcontext — sem estado global compartilhado entre threads.
    """
    if "db" not in g:
        db = sqlite3.connect(current_app.config["DB_PATH"])
        db.row_factory = sqlite3.Row
        g.db = db
    return g.db


def close_db(e=None):
    """Fecha a conexão da requisição, se existir."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
