from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import config_map
from flask_jwt_extended import JWTManager
import os
from flask_restx import Api

db = SQLAlchemy()
jwt  = JWTManager()

authoizations = {
    "Bearer Auth" : {
        "type":"apiKey",
        "in" :"header",
        "name" :"Authorization",
        "description":"Add Bearer <JWT Token>"
    }
}

api = Api(
    title="Contact App API",
    version="1.0.0",
    description="This is API docs for contact app",
    doc="/docs",
    authorizations=authoizations,
    security="Bearer Auth"
)

def create_app():
    app = Flask(__name__) 
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_map[env])

    #export FLASK_ENV=staging && flask run

    db.init_app(app)
    jwt.init_app(app)
    api.init_app(app)


    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint

    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(main_blueprint)
    
    from .main.routes import contact_ns
    from .auth.routes import auth_ns

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(contact_ns, path="/contacts")

    return app