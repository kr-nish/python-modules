from flask import request, jsonify
from flask_jwt_extended import create_access_token
from ..models import User, db
from . import auth
from .. import api
from flask_restx import Namespace, Resource, fields

auth_ns = Namespace("Auth", description="User Auth APIs")

signup_model = auth_ns.model("Signup", {
    "username": fields.String(required=True, description="Username"),
    "password": fields.String(required=True, description="Password"),
})

login_model = auth_ns.model("Login", {
    "username": fields.String(required=True, description="Username"),
    "password": fields.String(required=True, description="Password"),
})

#Signup route or how to create an account
@auth_ns.route("/signup")
class Signup(Resource):
    @auth_ns.expect(signup_model)
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error" :"Username and password required"}, 400

        if User.query.filter_by(username=username).first():
            return {"error" :"Username already exists "}, 409

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {"Message" : "User created successfully"}, 201

@auth_ns.route("/login")
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            token = create_access_token(identity=user.id)
            return {"token": token}, 200
        return {"error":"invalid credentials"}, 401