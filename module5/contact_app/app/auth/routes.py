from flask import request, jsonify
from flask_jwt_extended import create_access_token
from ..models import User, db
from . import auth

#Signup route or how to create an account
@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error" :"Username and password required"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error" :"Username already exists "}), 409
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message" : "User created successfully"}), 201

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity=user.id)
        return jsonify({"token": token}), 200
    return jsonify({"error":"invalid credentials"}), 401