from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        if not get_jwt()["admin"]:
            return jsonify({"message": "Only admin can access this endpoint"}), 401
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        if get_jwt()["admin"]:
            return jsonify({"message": "Login as user to access this endpoint"}), 401
        return f(*args, **kwargs)
    return decorated_function