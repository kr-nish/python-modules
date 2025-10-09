from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static") 
    app.config.from_object(Config)
    db.init_app(app)

    from .routes import main
    app.register_blueprint(main, url_prefix="")

    with app.app_context():
        db.create_all()

    return app