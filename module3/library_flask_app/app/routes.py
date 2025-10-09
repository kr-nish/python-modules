from flask import Blueprint, request, jsonify
from .models import Book
from . import db

main = Blueprint("main", __name__)

# Read all the books we have
@main.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books]), 200

# Add a book
@main.route("/books",methods= ["POST"])
def add_book():
    data = request.get_json()
    new_book = Book(title=data["title"], author=data["author"], year=data["year"])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book has been added successfully "}), 201

# to get a single book 
@main.route("/books/<int:id>", methods=["GET"])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify(book.to_dict()), 200

#Delete a book # to get a single book 
@main.route("/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message" :"Book has been successfully deleted"}), 200

#Update the book 
@main.route("/books/<int:id>", methods=["PUT"])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.year = data.get("year", book.year)
    db.session.commit()
    return ({"message: Book has been successfully updated "}), 200