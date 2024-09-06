import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.urandom(24)

def init_db(app):
    db = SQLAlchemy(app)
    with app.app_context():
        db.create_all()
    return db

def check_db_connection(db):
    try:
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False
