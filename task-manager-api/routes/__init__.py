from routes import category_routes, geral, report_routes, task_routes, user_routes


def register_blueprints(app):
    app.register_blueprint(geral.bp)
    app.register_blueprint(task_routes.bp)
    app.register_blueprint(user_routes.bp)
    app.register_blueprint(report_routes.bp)
    app.register_blueprint(category_routes.bp)
