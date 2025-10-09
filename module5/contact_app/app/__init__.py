from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt  = JWTManager()

def create_app():
    app = Flask(__name__) 
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)


    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(main_blueprint)
    

    return app