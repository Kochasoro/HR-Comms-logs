from flask import Flask
from app.extensions import db, login_manager, migrate
from app.config import Config
from app import models
from app.models.settings import SystemSettings
from app.routes.secretary import secretary_bp
from app.routes.auth import auth_bp   
from app.routes.admin import admin_bp
from app.seed_memo import seed_memos 
from .routes.main import main
from app.models.user import User   
from app.seed import seed_command  

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    app.register_blueprint(secretary_bp)
    app.register_blueprint(admin_bp)

    # ✅ Register CLI command
    app.cli.add_command(seed_command)
    app.cli.add_command(seed_memos)

    @app.context_processor
    def inject_settings():
        settings = SystemSettings.query.first()
        return dict(settings=settings)
    
    print(app.url_map)

    return app