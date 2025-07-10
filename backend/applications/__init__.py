from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from applications.models import db, User
from config import Config
from flask import request, jsonify

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app, origins=["http://localhost:8081"], supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    print("🚨 Unauthorized access hit — user is not logged in")
    print("🔍 Request headers:", dict(request.headers))
    print("🔍 Request cookies:", request.cookies)
    return jsonify({"message": "Unauthorized"}), 401


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

from applications import routes  # 👈 Now safe to import