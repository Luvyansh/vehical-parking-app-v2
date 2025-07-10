from applications import app, db, User

def create_admin():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(admin=True).first():
            user = User(name="Admin", username="admin", email="admin@park.com", password="22f1000812")
            user.admin = True
            db.session.add(user)
            db.session.commit()

create_admin()

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)