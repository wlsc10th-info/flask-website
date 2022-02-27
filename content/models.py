from operator import index
from numpy import False_
from sqlalchemy import null
from content import db,login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSON
import os
#import cv2
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    image    = db.Column(JSON)
    id       = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64),unique=True, index=True)
    password_hash = db.Column(db.String(128))
    showing_img_name=db.Column(db.String(64))
    def __init__(self, username, password):
        """初始化"""
        self.showing_img_name=None
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.image = {"name":[],"path":[]}
    
    def check_password(self, password):
        """檢查使用者密碼"""
        return check_password_hash(self.password_hash, password)
    def input_images(self,image_path,name):
        self.image["name"].append(name)
        self.image["path"].append(image_path)
        print('name:',self.image["name"])
        
        return
    def delete_image(self,image_path,name):
        self.image["name"].remove(name)
        self.image["path"].remove(image_path)
        
        return
    def filename(self,path):
        if path==None:
            return
        basename=os.path.basename(path)
        filename=os.path.splitext(basename)[0]
        return filename
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)