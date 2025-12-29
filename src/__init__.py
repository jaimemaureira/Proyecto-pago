from datetime import timedelta
import os
from flask import Flask
from .api import api_bp
from .config import Config
from .routes import main_bp
from .extensions import db, mail, csrf

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["WTF_CSRF_TIME_LIMIT"] = 60 * 60 * 6  # 6 horas
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=6)
    
    print("DB URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    # Init extensions
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app

