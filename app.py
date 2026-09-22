from flask import Flask

from config import Config
from extensions import db, login_manager
from models import Usuario


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from auth import auth_bp
    from admin import admin_bp
    from portal import portal_bp
    from agendamentos import agendamentos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(portal_bp)
    app.register_blueprint(agendamentos_bp)

    @app.route("/")
    def index():
        from flask import redirect, url_for
        return redirect(url_for("auth.login"))

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    |#app.run(debug=True)
    app.run(host="0.0.0.0", debug=True)
