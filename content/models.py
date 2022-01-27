from operator import index
from numpy import False_
from sqlalchemy import null
from content import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json
#import cv2
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    image_path_1    = db.Column(db.String(64))
    image_path_2    = db.Column(db.String(64))
    image_path_3    = db.Column(db.String(64))
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    showing_num='0'
    def __init__(self, username, password):
        """初始化"""
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """檢查使用者密碼"""
        return check_password_hash(self.password_hash, password)
    def input_images(self,image_path):
        if self.image_path_1==None:
            print('I save image_path_1')
            self.image_path_1=image_path
            return
        elif self.image_path_2==None:
            print("I asve Image_path_2")
            self.image_path_2=image_path
            return
        else:
            print("I save Image_path_3")
            self.image_path_3=image_path
            return
    def delete_image(self,image_num):
        if image_num ==1:
            self.image_path_1=None
            return
        elif image_num==2:
            self.image_path_2=None
            return
        else:
            self.image_path_3=None
            return
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)