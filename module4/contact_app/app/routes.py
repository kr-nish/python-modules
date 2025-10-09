from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from . import db
from .models import Contact

main = Blueprint("main", __name__, template_folder="templates")

#get all books 
@main.route("/", methods=["GET"])
def index():
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template("index.html", contacts=contacts)

@main.route("/add", methods=["GET","POST"])
def add_contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        if not name:
            return render_template("add_contact.html", error="Name is required", name=name, email=email, phone=phone)
        new = Contact(name=name, email=email, phone=phone)
        db.session.add(new)
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("add_contact.html")


#Edit Contact
@main.route("/edit/<int:contact_id>", methods=["GET","POST"])
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    if request.method == "POST":
        contact.name = request.form.get("name", contact.name)
        contact.email = request.form.get("email", contact.email)
        contact.phone = request.form.get("phone", contact.phone)
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("edit_contact.html", contact=contact)

#Delete contact
@main.route("/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for("main.index"))

#JSON API ENDpoint

@main.route("/api/contacts",methods=["GET"])
def api_contacts():
    contacts = [c.to_dict() for c in Contact.query.all()]
    resp = jsonify(contacts)
    resp.status_code = 200
    resp.headers["X-App=Name"]= "ContactBook"
    return resp

