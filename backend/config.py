import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///parking_db.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_to_a_strong_key")

    # 🧠 These are REQUIRED for cookie-based auth across ports (CORS)
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False # Use True if using HTTPS