from flask_bcrypt import Bcrypt
from flask import Flask
from flask_cors import CORS
from applications.models import db, User
from config import Config
from sqlalchemy import event
from sqlalchemy.engine import Engine

bcrypt = Bcrypt()
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Enable FK constraints in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

CORS(app, supports_credentials=True)

from applications import routes