from numpy import False_
from content import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
#import cv2
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    image_path    = db.Column(db.String(64))
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    def __init__(self, username, password):
        """初始化"""
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """檢查使用者密碼"""
        return check_password_hash(self.password_hash, password)
    def input_image(self,image_path):
         self.image_path=image_path
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)