from flask import request, jsonify
from applications.models import *
from app import app

@app.route("/", methods=["GET"])
def index():
    return "Hello, World!"

#Register users
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    #Check if user already exists
    check_user = db.session.query(User).filter_by(email=email).first()
    if check_user:
        return jsonify({"message": "User already exists"}), 400

    user = User(name=name, username=username, email=email, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error registering user"}), 500

#User login
from flask_jwt_extended import create_access_token

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = db.session.query(User).filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity={"username": user.username, "admin": user.admin})
        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "admin": user.admin
        }), 200
    return jsonify({"message": "Invalid credentials"}), 401

from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/admin_dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    identity = get_jwt_identity()
    if not identity['admin']:
        return jsonify({"message": "Unauthorized"}), 403
    return jsonify({"message": "Welcome Admin!"})