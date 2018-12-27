# -*- coding:utf-8 -*-

__author__ = u'Jiang Wen'
from flask import render_template, flash, request, abort, redirect, url_for, g, jsonify
from app import app, db, lm, DEBUGGING  # , csv_set
from flask_login import login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from app.models import test_init, User
from app.forms import LoginForm
from sqlalchemy.sql import and_
from sqlalchemy import func
import json
import requests

Bootstrap(app)


@app.before_first_request
def init_view():
    # Uncomment to recreate database every time
    db.drop_all()
    db.create_all()  # Do not recreate mysql database.
    test_init()
    db.session.commit()

    # Add login guider
    lm.login_view = url_for('login')
    lm.login_message = "Please login"
    lm.login_message_category = 'info'


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(uid):
    return User.query.get(uid)


@app.route('/index.html')
def index():
    # flash ( 'Hello %s, you have logged in.' % current_user.get_id (), 'success' )
    return render_template("index.html")


@app.route('/Tindex.html')
def Tindex():
    # flash ( 'Hello %s, you have logged in.' % current_user.get_id (), 'success' )
    return render_template("Tindex.html")


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/courseDemo.html')
def courseDemo():
    return render_template('courseDemo.html')


@app.route('/forum.html')
def forum():
    return render_template('forum.html')


@app.route('/homework.html')
def homework():
    return render_template('homework.html')


@app.route('/homeworkDemo.html')
def homeworkDemo():
    return render_template('homeworkDemo.html')


@app.route('/info.html')
def info():
    return render_template('info.html')


@app.route('/media.html')
def media():
    return render_template('media.html')


@app.route('/signUp.html')
def signUp():
    return render_template('signUp.html')


@app.route('/TcourseDemo.html')
def TcourseDemo():
    return render_template('TcourseDemo.html')


@app.route('/Thomework.html')
def Thomework():
    return render_template('Thomework.html')


@app.route('/Tinfo.html')
def Tinfo():
    return render_template('Tinfo.html')


@app.route('/Tmedia.html')
def Tmedia():
    return render_template('Tmedia.html')


@app.route('/signUp.html')
def signUpp():
    return render_template('signUp.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if g.user is not None and g.user.is_authenticated:
        flash("You have logged in to system")
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(id=form.username.data).first()
            if user is None:
                error = 'Invalid username'
            elif not user.check_password_hash(form.password.data):
                error = 'Invalid password'
            else:
                login_user(user=user, remember=form.remember.data)
                return redirect(url_for('index'))
        except Exception as e:
            # flash ( 'login fail', 'primary' )
            flash(e, 'danger')

    elif request.method == 'POST':
        flash('Invalid input', 'warning')
    if error is not None:
        flash(error, category='danger')
    return render_template('login.html', form=form, error=error)
