# 引入Form基类
from flask_wtf import FlaskForm
# 引入Form元素父类
from wtforms import StringField, PasswordField, BooleanField, IntegerField, FloatField, SelectField, DecimalField, \
    SubmitField
# 引入Form验证父类
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileRequired

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


class AddCourseForm(FlaskForm):
    coursename = StringField("coursename", validators=[DataRequired()])
    description = StringField("description", validators=[DataRequired()])
    courseID = StringField("courseID", validators=[DataRequired()])
    time = StringField("time", validators=[DataRequired()])
    picture = FileField('picture', validators=[FileRequired()])
    submit = SubmitField('submit')


class AddStudentForm(FlaskForm):
    picture = FileField('upload', validators=[FileRequired()])
    submit = SubmitField('submit')


class HomeworkForm(FlaskForm):
    course_id = StringField("course_id", validators=[DataRequired()])


class AddMessageForm(FlaskForm):
    content = StringField("content", validators=[DataRequired()])


class AddPostForm(FlaskForm):
    title = StringField("title", validators=[DataRequired()])
    content = StringField("content")
