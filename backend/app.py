from flask import Flask

from models import *
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def create_admin():
    check_admin = db.session.query(User).filter_by(admin=True).first()
    if check_admin:
        return
    else:
        # Create the admin user
        user = User(name="Park Admin", username="admin", email="admin@park.com", password="22f1000812")
        # Set the admin flag to True since the constructor has no admin as a parameter
        user.admin = True
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error creating admin:", str(e))

with app.app_context():
    db.create_all()
    create_admin()

@app.route("/", methods=["GET"])
def index():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)