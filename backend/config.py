from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'parking_db.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'