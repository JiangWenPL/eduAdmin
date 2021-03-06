# coding: utf-8
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import json
import requests
import datetime
# from sqlalchemy import CHAR, Column, DECIMAL, ForeignKey, INTEGER, String, TIMESTAMP, text
# from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import and_
from datetime import datetime


# Base = declarative_base ()
# metadata = Base.metadata


# BaseModel = declarative_base ()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(32))
    password_hash = db.Column(db.String(32))
    user_type = db.Column(db.String(32))
    email = db.Column(db.String(32))
    description = db.Column(db.String(256))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __init__(self, id, name, password, email, user_type, is_root=False):
        self.id = id
        self.name = name
        self.password = password
        self.email = email
        self.user_type = user_type
        self.is_root = is_root
        self.description = ''

    @property
    def password(self):
        raise AttributeError("Password unaccessible")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    # For debug
    def __repr__(self):
        return '<User %r>' % self.id


class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(32))
    teacher_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    course_url = db.Column(db.String(128))  # preview picture
    time = db.Column(db.String(32))
    description = db.Column(db.String(256))

    def __init__(self, id, name, teacher_id, course_url, time, description):
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.course_url = course_url
        self.time = time
        self.description = description

    def __repr__(self):
        return '<Course %r>' % self.id


class TakingClass(db.Model):
    __tablename__ = "takingClass"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(32), db.ForeignKey("course.id"))
    student_id = db.Column(db.String(32), db.ForeignKey("user.id"))

    def __init__(self, course_id, student_id):
        self.course_id = course_id
        self.student_id = student_id

    def __repr__(self):
        return '<TakingClass %r>' % self.id


class Homework(db.Model):
    __tablename__ = "homework"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    course_id = db.Column(db.String(32), db.ForeignKey("course.id"))
    description = db.Column(db.String(256))
    deadline = db.Column(db.DateTime)

    def __init__(self, name, course_id, description, deadline):
        self.name = name
        self.course_id = course_id
        self.description = description
        self.deadline = deadline

    def __repr__(self):
        return '<Homework %r>' % self.id


class StudentHomework(db.Model):
    __tablename__ = "studentHomework"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    homework_id = db.Column(db.Integer, db.ForeignKey("homework.id"))
    student_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    homework_url = db.Column(db.String(128))
    grade = db.Column(db.Integer, default=-1)  # grade == -1 means that the homework hasn't been marked

    def __init__(self, homework_id, student_id, homework_url):
        self.student_id = student_id
        self.homework_id = homework_id
        self.homework_url = homework_url
        self.grade = -1


# a post in bbs
class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_topic = db.Column(db.String(32))
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    description = db.Column(db.String(256), default="")
    # a course is corresponding to a module
    course_id = db.Column(db.String(32), db.ForeignKey("course.id"))
    create_time = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, post_topic, user_id, course_id, description=''):
        self.post_topic = post_topic
        self.course_id = course_id
        self.user_id = user_id
        self.description = description

    def __repr__(self):
        return '<Post %r>' % self.id


class Message(db.Model):  # A floor in a post
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    description = db.Column(db.String(256))
    floor = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, post_id, user_id, description, floor):
        self.post_id = post_id
        self.user_id = user_id
        self.description = description
        self.floor = floor

    def __repr__(self):
        return '<message %r>' % self.id


class ClassInformation(db.Model):
    __tablename__ = "ClassInformation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(32), db.ForeignKey("course.id"))
    content = db.Column(db.String(256))
    time = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, course_id, content):
        self.course_id = course_id
        self.content = content


class Media(db.Model):
    __tablename__ = "Media"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    course_id = db.Column(db.String(32), db.ForeignKey("course.id"))
    url = db.Column(db.String(128))

    def __init__(self, name, course_id, url):
        self.name = name
        self.course_id = course_id
        self.url = url


def test_init():
    db.session.add(User('200001', 'Alice', '123', '000001@zju.edu.cn', 'student'))
    db.session.add(User('200002', 'Bob', '123', '000002@zju.edu.cn', 'student'))
    db.session.add(User('200003', 'Cindy', '123', '000003@zju.edu.cn', 'student'))
    db.session.add(User('100001', 'Mr. Li', '123', '100001@zju.edu.cn', 'teacher'))
    db.session.add(
        Course('cs001', 'Java应用技术', '100001', '../static/uploads/class2.jpg', 'Monday 8:00', 'This course will teach Java.'))
    db.session.add(TakingClass('cs001', '200001'))
    db.session.add(Homework('MiniCAD', 'cs001', 'A MiniCAD in Java', datetime(2019, 2, 1, 10, 10, 10)))
    db.session.add(StudentHomework(1, '200001', '../static/uploads/class2.jpg'))
    db.session.add(Post('The homework is so hard!', '200001', 'cs001'))
    db.session.add(Message(1, '200001', 'Can you help me?', 1))
    db.session.add(ClassInformation('cs001', 'Do not forget to submit your homework!'))
