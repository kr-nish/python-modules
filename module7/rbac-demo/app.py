from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User
from config import Config
from decorators import role_required
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

@app.before_request
def create_tables():
    db.create_all()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute"],
    app=app
)
#signup or create account 
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    if User.query.filter_by(username=username).first():
        return {"Error" : "User already exists"}, 400
    
    new_user = User(username=username, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return {"message": f"User {username} created with this {role}"}, 201

#login route
@app.route("/login", methods={"POST"})
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username = username).first()
    if user and user.check_password(password):
        token = create_access_token(identity=user.id)
        return {"token": token}, 200
    
    return {"error" : "Invalid credentials"}, 401 

@app.route("/dashboard", methods=["GET"])
@jwt_required()
@limiter.limit("3 per minute") #Custom rate limiting
def dashboard():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return {"message": f"Welcome {user.username}! your role is {user.role}"}

@app.route("/admin", methods=["GET"])
@jwt_required()
@role_required("admin")
def admin_only():
    return {"message":"If you can see this you are an admin congrats!!!"}

if __name__ == "__main__":
    app.run(debug=True)