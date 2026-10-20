from routes import admin, geral, pedidos, produtos, relatorios, usuarios


def register_blueprints(app):
    app.register_blueprint(produtos.bp)
    app.register_blueprint(usuarios.bp)
    app.register_blueprint(pedidos.bp)
    app.register_blueprint(relatorios.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(geral.bp)
