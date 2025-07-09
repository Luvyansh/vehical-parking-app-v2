from flask import Flask
from applications.models import db, User
from config import Config
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

CORS(app, supports_credentials=True)

from flask_jwt_extended import JWTManager

app.config['JWT_SECRET_KEY'] = 'vehical-parking'  # Change this to an environment variable in production
jwt = JWTManager(app)

# Importing routes after 'app' is created and configured
from applications.routes import *

def create_admin():
    with app.app_context():
        db.create_all()
        check_admin = db.session.query(User).filter_by(admin=True).first()
        if check_admin:
            return
        else:
            user = User(name="Park Admin", username="admin", email="admin@park.com", password="22f1000812")
            user.admin = True
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print("Error creating admin:", str(e))

create_admin()

if __name__ == "__main__":
    app.run(debug=True)