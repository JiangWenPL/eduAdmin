# -*- coding:utf-8 -*-
__author__ = u'Jiang Wen'
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import *;

# from flask_uploads import UploadSet, configure_uploads, DATA
import os

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
DEBUGGING = False


app.config['UPLOADED_PHOTO_DEST'] = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOADED_PHOTO_ALLOW'] = IMAGES
photos = UploadSet('PHOTO')

configure_uploads(app, photos)
# app.config.from_object ( Config () )
# scheduler.api_enabled = True
from app import models, views
