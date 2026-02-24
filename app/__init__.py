from flask import Flask
from app.extensions import db, login_manager, migrate
from app.config import Config
from app import models
from app.routes.secretary import secretary_bp
from .routes.main import main
from app.models.user import User   

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(main)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)   

    print(app.url_map)

    login_manager.login_view = "main.home"  
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    app.register_blueprint(secretary_bp)
    return app