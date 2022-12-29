from datetime import datetime
from time import time
from flask_login import UserMixin
import jwt
from blogapp import db, login_manager
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    
    def get_reset_token(self, expires_sec=18000):
        return jwt.encode({"reset_password": self.id, "exp": time() + expires_sec}, current_app.config["SECRET_KEY"], algorithm="HS256")
        
    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])["reset_password"]
        except:
            return None
        return User.query.get(user_id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(130), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(), default=datetime.utcnow, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Post {self.title}, {self.date_posted}"
