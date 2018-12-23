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



def test_init():
    pass