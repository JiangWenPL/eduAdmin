# 引入Form基类
from flask_wtf import FlaskForm
# 引入Form元素父类
from wtforms import StringField, PasswordField, BooleanField, IntegerField, FloatField, SelectField, DecimalField
# 引入Form验证父类
from wtforms.validators import DataRequired, Length, NumberRange, Optional

# from flask_wtf.file import FileAllowed, FileRequired, FileField
# from app import csv_set
# from app.models import Book

__author__ = 'JiangWen'


class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember = BooleanField("remember", validators=[Optional()], default=False)


class SignUpForm(FlaskForm):
    user = StringField("user", validators=[DataRequired()])
    name = StringField("name", validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    userType = StringField("userType", validators=[DataRequired()])
