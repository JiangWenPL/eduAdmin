# -*- coding:utf-8 -*-

__author__ = u'Jiang Wen'
from flask import render_template, flash, request, abort, redirect, url_for, g, jsonify
from app import app, db, lm, DEBUGGING  # , csv_set
from flask_login import login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from app.models import test_init, User, Course, Homework, TakingClass, StudentHomework, Post, Message
from app.forms import *
from flask_uploads import *
from werkzeug.utils import secure_filename
from sqlalchemy.sql import and_
from sqlalchemy import func, desc
import json
import requests
from easydict import EasyDict

Bootstrap(app)


@app.before_first_request
def init_view():
    # Uncomment to recreate database every time
    db.drop_all()
    db.create_all()  # Do not recreate mysql database.
    test_init()
    db.session.commit()

    print(User.query.all())
    print(Course.query.all())
    print(Homework.query.all())
    print(TakingClass.query.all())
    print(Post.query.all())
    print(Message.query.all())

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


class Total:
    def __init__(self, name, teacher, time, imgUPL, courseDetail, id):
        self.name = name
        self.teacher = teacher
        self.time = time
        self.imgURL = imgUPL
        self.courseDetail = courseDetail
        self.id = id


@app.route('/index.html')
@login_required
def index():
    flash('Hello, test flash', 'success')
    user_type2index = {'teacher': 'Tindex.html', 'student': 'index.html'}
    if g.user.user_type != 'student':
        redirect(user_type2index[g.user.user_type])
    # print(g.user.email)
    takings = TakingClass.query.filter_by(student_id=g.user.id).all()

    courses = []
    for taking in takings:
        course = Course.query.filter_by(id=taking.course_id).first()
        courses.append(course)

    # class Total:
    #     def __init__(self, name, teacher, time, imgUPL, courseDetail):
    #         self.name = name
    #         # self.location = "location"
    #         self.teacher = teacher
    #         self.time = time
    #         self.imgURL = imgUPL
    #         self.courseDetail = courseDetail

    # flash ( 'Hello %s, you have logged in.' % current_user.get_id (), 'success' )

    total = []
    for course in courses:
        onecourse = Total(course.name, course.teacher_id, course.time, course.course_url, course.description, course.id)
        total.append(onecourse)
    return render_template("index.html", Total=total)


@app.route('/Tindex.html', methods=['GET', 'POST'])
@login_required
def Tindex():
    # Tindex.html?course_id=12341234
    print(request.data)
    print(app.config['UPLOADED_PHOTO_DEST'])
    form = AddCourseForm()
    # flash ( 'Hello %s, you have logged in.' % current_user.get_id (), 'success' )
    flash('Hello, test flash', 'success')
    courses = Course.query.filter_by(teacher_id=g.user.id).all()
    total = []
    for course in courses:
        onecourse = Total(course.name, course.teacher_id, course.time, course.course_url, course.description, course.id)
        total.append(onecourse)

    if form.validate_on_submit():
        print("a")
        try:
            # print("b")
            course = Course.query.filter_by(id=form.courseID.data).first()
            if not course is None:
                error = 'Course has registered!'
                return render_template('Tindex.html')
            else:
                # filename = form.picture.data.filename
                filename = secure_filename(form.picture.data.filename)
                # print(filename)
                # print(app.config['UPLOADED_PHOTO_DEST'])
                # 将上传的文件保存到服务器;
                # form.picture.data.save(app.config['UPLOADED_PHOTO_DEST'], filename)
                # os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form.picture.data.save(os.path.join(app.config['UPLOADED_PHOTO_DEST'], filename))
                db.session.add(
                    Course(form.courseID.data, form.coursename.data, g.user.id,
                           'static/uploads/' + filename, form.time.data,
                           form.description.data))
                db.session.commit()
                print(Course.query.all())
                flash('The course is added successfully!')
                return redirect(url_for('Tindex'))
        except Exception as e:
            flash(e, 'danger')
    return render_template("Tindex.html", Total=total, form=form)


@app.route('/contact.html')
@login_required
def contact():
    return render_template('contact.html', form=LoginForm())  # Temporary to make it run


@app.route('/courseDemo.html')
@login_required
def courseDemo():
    try:
        course_id = request.args.get('course_id')
    except:
        flash("Please specify course_id")
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))
    # print(course_id
    course = Course.query.filter_by(id=course_id).first()

    class CourseInfo:
        def __init__(self, name, details):
            self.name = name
            self.details = details

    return render_template('courseDemo.html', courseInfo=CourseInfo(course.name, course.description))


@app.route('/forum.html')
@login_required
def forum():
    # class Total:
    #     def __init__(self):
    #         self.name = 'This is name'
    #         self.id = 'This is id'
    #         self.details = 'This is details balabala'

    course_id = request.args.get('course_id', None)
    if not course_id:
        if g.user.user_type == 'student':
            course_id = TakingClass.query.filter_by(student_id=g.user.get_id()).one().course_id
        else:
            course_id = Course.query.filter_by(teacher_id=g.user.get_id()).one().id
    posts = list()
    if course_id:
        posts = db.session.query(User, Post).join(Post).filter(Post.course_id == course_id).order_by(
            desc(Post.create_time)).limit(10).all()
    total = [EasyDict(name=i.User.name, id=i.User.id, details=i.Post.post_topic) for i in posts]
    return render_template('forum.html', Total=total, Courses=Course.query.all())


@app.route('/homework.html')
@login_required
def homework():
    class HomeworkInfo:
        def __init__(self):
            self.name = 'This is name'
            self.url = "homeworkDemo.html"
            self.grade = 99

    return render_template('homework.html', Total=[HomeworkInfo()] * 10)


@app.route('/homeworkDemo.html')
@login_required
def homeworkDemo():
    class HomeworkInfo:
        def __init__(self):
            self.name = 'This is name'
            self.details = "fdasfasdfasdfasdfasd"

    return render_template('homeworkDemo.html', homework=HomeworkInfo())


@app.route('/info.html')
@login_required
def info():
    class Info:
        def __init__(self):
            self.name = 'This is name'
            self.details = "fdasfasdfasdfasdfasd"

    return render_template('info.html', Total=[Info()] * 10)


@app.route('/media.html')
@login_required
def media():
    class Info:
        def __init__(self):
            self.url = 'courseDemo'
            self.img = "../static/uploads/course_01.jpg"

    return render_template('media.html', Total=[Info()] * 10)


@app.route('/signUp.html', methods=['GET', 'POST'])
def signUp():
    form = SignUpForm()
    # print("aaaaa")
    if form.validate_on_submit():
        # print("OK!!")
        try:
            user = User.query.filter_by(id=form.user.data).first()
            if not user is None:
                error = 'User has registered!'
                return render_template('signUp.html')
            else:
                db.session.add(
                    User(form.user.data, form.name.data, form.password.data, form.email.data, form.userType.data))
                db.session.commit()
        except Exception as e:
            flash(e, 'danger')

        print(User.query.all())
    return render_template('signUp.html', form=form)


@app.route('/TcourseDemo.html')
@login_required
def TcourseDemo():
    try:
        course_id = request.args.get('course_id')
    except:
        flash("Please specify course_id")
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))
    # print(course_id
    course = Course.query.filter_by(id=course_id).first()

    class CourseInfo:
        def __init__(self, name, details):
            self.name = name
            self.details = details

    form = AddStudentForm()
    if form.validate_on_submit():
        try:
            print('TcourseDemo')
            filename = secure_filename(form.upload.data.filename)
            for line in form.upload.data:
                line = form.upload.data.readline()


        except Exception as e:
            flash(e, 'danger')

    return render_template('courseDemo.html', courseInfo=CourseInfo(course.name, course.description))


@app.route('/Thomework.html')
@login_required
def Thomework():
    return render_template('Thomework.html')


@app.route('/TInfo.html')
@login_required
def Tinfo():
    return render_template('Tinfo.html')


@app.route('/Tmedia.html')
@login_required
def Tmedia():
    return render_template('Tmedia.html')


# @app.route('/signUpp.html')
# def signUpp():
#     return render_template('signUp.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
@app.route('/login.html', methods=['GET', 'POST'])
def login():
    error = None
    # if g.user is not None and g.user.is_authenticated:
    #     flash("You have logged in to system")
    #     return redirect(url_for('index'))
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
                print(user.user_type)
                if user.user_type == 'student':
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for("Tindex"))
        except Exception as e:
            # flash ( 'login fail', 'primary' )
            flash(e, 'danger')

    elif request.method == 'POST':
        flash('Invalid input', 'warning')
    if error is not None:
        flash(error, category='danger')
    return render_template('login.html', form=form, error=error)


@app.route('/logout')
@login_required
def logout():
    logout_user()  # 登出用户
    flash("Logout successful", category='success')
    return redirect(url_for('index'))


@app.route('/teacherInfo.html', methods=['GET', 'POST'])
def teacherInfo():
    try:
        teacher_id = request.args.get('teacher_id')
    except:
        flash("Please specify teacher_id")
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))

    teacher = User.query.filter_by(id=teacher_id).first()
    if teacher is None:
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))

    print(teacher)

    class TeachInfo:
        def __init__(self, name, details, email):
            self.name = name
            self.details = details
            self.email = email

    return render_template('teacherInfo.html', teachInfo=TeachInfo(teacher.name, teacher.description, teacher.email))
