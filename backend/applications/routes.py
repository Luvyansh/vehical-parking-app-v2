from flask import request, jsonify, session, make_response
from flask_cors import cross_origin
from flask_login import login_user, logout_user, login_required, current_user
from applications.models import *
from app import app

@app.route("/", methods=["GET"])
def index():
    return "Hello, World!"

# ✅ User registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400

    user = User(name=name, username=username, email=email, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error registering user"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)  # sets the session cookie
        user.last_login = datetime.now()
        db.session.commit()

        response = make_response(jsonify({
            "message": "Login successful",
            "admin": user.admin
        }))
        print("✅ login_user() called successfully")
        print("📤 Response headers that will be sent:", dict(response.headers))
        return response

    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/check_cookie")
def check_cookie():
    print("🔍 Request cookies:", request.cookies)
    return jsonify({"cookies": dict(request.cookies)}), 200

# ✅ Logout
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

# ✅ Admin dashboard (only if logged in + is admin)
@app.route("/admin_dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    if not current_user.admin:
        return jsonify({"message": "Unauthorized"}), 403
    return jsonify({"message": f"Welcome Admin {current_user.username}!"}), 200

# ✅ User dashboard (only if logged in + not admin)
@app.route("/user_dashboard", methods=["GET"])
@login_required
def user_dashboard():
    print("🧠 Current user authenticated:", current_user.is_authenticated)
    print("🧠 Current user:", current_user)
    if current_user.admin:
        return jsonify({"message": "Admin is not allowed here"}), 403
    return jsonify({"message": f"Welcome {current_user.username}!"}), 200