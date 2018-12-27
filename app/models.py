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


# Base = declarative_base ()
# metadata = Base.metadata


# BaseModel = declarative_base ()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(32), primary_key=True)
    password_hash = db.Column(db.String(32))
    user_type = db.Column(db.String(32), default="guest")

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __init__(self, id, name, password, is_root=False):
        self.id = id
        self.name = name
        self.password = password
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


def test_init():
    db.session.add(User('316010', 'Alice', '123'))
