from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, email_validator
from wtforms import ValidationError
from content.models import User

class LoginForm(FlaskForm):
    username = StringField('使用者帳號', validators=[DataRequired()])
    password = PasswordField('密碼',validators=[DataRequired()])
    submit = SubmitField('登入系統')

class RegistrationForm(FlaskForm):
    username = StringField('使用者帳號', validators=[DataRequired()])
    password = PasswordField('密碼', validators=[DataRequired(), EqualTo('pass_confirm', message='密碼需要吻合')])
    pass_confirm = PasswordField('確認密碼', validators=[DataRequired()])
    submit = SubmitField('註冊')
    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('使用者名稱已經存在')