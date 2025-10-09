from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Contact, db
from . import main

@main.route("/contacts", methods=["GET"])
@jwt_required()
def get_contacts():
    user_id = get_jwt_identity()
    contacts = Contact.query.filter_by(user_id=user_id).all()
    return jsonify([c.to_dict() for c in contacts]), 200


@main.route("/contacts", methods=["POST"])
@jwt_required()
def add_contact():
    user_id = get_jwt_identity()
    data = request.get_json()
    new_contact = Contact(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        user_id=user_id
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"message": "Contact added"}), 201