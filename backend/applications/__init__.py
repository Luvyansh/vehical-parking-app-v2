from flask_bcrypt import Bcrypt
from flask import Flask
from flask_cors import CORS
from applications.models import db, User
from config import Config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from tools import workers
from tools.mail_bot import init_app, send_email
import os

bcrypt = Bcrypt()
from flask_jwt_extended import JWTManager

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))

# Initialize Flask app, explicitly telling it where the templates are
app = Flask(__name__, template_folder=template_dir) # <--- MODIFIED THIS LINE
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

init_app(app)

celery = workers.celery
celery.conf.update(
    broker_url=app.config["CELERY_BROKER_URL"],
    result_backend=app.config["CELERY_RESULT_BACKEND"],
)

celery.Task = workers.ContextTask

# Enable FK constraints in SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

CORS(app, supports_credentials=True)

app.app_context().push()

from applications import routes