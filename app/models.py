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
    password_hash = db.Column(db.String(32))
    user_type = db.Column(db.String(32))
    email = db.Column(db.String(32))

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

    def __init__(self, id, name, teacher_id, course_url, time):
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.course_url = course_url
        self.time = time

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


# a post in bbs
class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_topic = db.Column(db.String(32))
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    # a course is corresponding to a module
    course_id = db.Column(db.String(32), db.ForeignKey("course.id"))

    def __init__(self, post_topic, user_id, course_id):
        self.post_topic = post_topic
        self.course_id = course_id
        self.user_id = user_id

    def __repr__(self):
        return '<Post %r>' % self.id


class Message(db.Model):  # A floor in a post
    __tablename__ = "message"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    description = db.Column(db.String(256))
    floor = db.Column(db.Integer)

    def __init__(self, post_id, user_id, description, floor):
        self.post_id = post_id
        self.user_id = user_id
        self.description = description
        self.floor = floor

    def __repr__(self):
        return '<message %r>' % self.id


def test_init():
    db.session.add(User('316010', 'Alice', '123', '316010@zju.edu.cn', 'student'))
    db.session.add(Course('cs221', 'NLP', 'teach001', '../static/uploads/class2.jpg', 'Friday'))
    db.session.add(TakingClass('cs221', '316010'))
    db.session.add(Homework('MiniCAD', 'cs221', 'A MiniCAD in Java', datetime(2012, 3, 3, 10, 10, 10)))
    db.session.add(Post('The homework is so hard!', '316010', 'cs221'))
    db.session.add(Message('1', '316010', 'Can you help me?', 1))
