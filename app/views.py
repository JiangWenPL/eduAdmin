# -*- coding:utf-8 -*-

__author__ = u'Jiang Wen'
from flask import render_template, flash, request, abort, redirect, url_for, g, jsonify
from app import app, db, lm, DEBUGGING  # , csv_set
from flask_login import login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap
from app.models import *
from app.forms import *
from flask_uploads import *
from werkzeug.utils import secure_filename
from sqlalchemy.sql import and_
from sqlalchemy import func, desc
from easydict import EasyDict
import csv
import json
import requests

Bootstrap(app)


@app.before_first_request
def init_view():
    # Uncomment to recreate database every time
    # db.drop_all()
    # db.create_all()  # Do not recreate mysql database.
    # test_init()
    # db.session.commit()

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
    teacher = True
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


@app.route('/forum.html', methods=['GET', 'POST'])
@login_required
def forum():
    form = AddPostForm()
    course_id = request.args.get('course_id', None)
    if not course_id:
        if g.user.user_type == 'student':
            course_id = TakingClass.query.filter_by(student_id=g.user.get_id()).one().course_id
        else:
            course_id = Course.query.filter_by(teacher_id=g.user.get_id()).one().id
    posts = list()
    if course_id:
        if request.method == 'POST' and form.validate_on_submit():
            db.session.add(Post(form.title.data, g.user.get_id(), course_id, form.content.data))
            db.session.commit()
        posts = db.session.query(User, Post).join(Post).filter(Post.course_id == course_id).order_by(
            desc(Post.create_time)).limit(10).all()
    total = [EasyDict(name=i.User.name, id=i.User.id, details=i.Post.post_topic, post_id=i.Post.id) for i in posts]
    return render_template('forum.html', Total=total, Courses=Course.query.all(), form=form)


@app.route('/forumInfo.html', methods=['GET', 'POST'])
@login_required
def forum_info():
    title = None
    post_id = request.args.get('post_id', None)
    form = AddMessageForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            floor_cnt = Message.query.filter_by(post_id=post_id).count()
            db.session.add(
                Message(post_id=post_id, user_id=g.user.get_id(), description=form.content.data, floor=floor_cnt + 1))
            db.session.commit()
        except Exception as e:
            if DEBUGGING:
                flash(e)
                print(e)
    if not post_id:
        flash('Please select a post', 'error')
        redirect(url_for('forum'))
    try:
        post = Post.query.filter_by(id=post_id).one()
        title = EasyDict(name=post.post_topic, details=post.description)
        messages = db.session.query(User, Message).join(Message).filter(Message.post_id == int(post_id)).order_by(
            desc(Message.time)).all()
    except Exception as e:
        if DEBUGGING:
            flash(e, 'error')
            print(e)
        return redirect(url_for(forum_info))
    total = [EasyDict(name=i.User.name, id=i.User.id, details=i.Message.description, num=i.Message.floor) for i in
             messages]
    return render_template('forumInfo.html', Total=total, Title=title, form=form)


@app.route('/homework.html', methods=['GET', 'POST'])
@login_required
def homework():
    if g.user.user_type == 'teacher':
        return redirect('Thomework.html')

    class CourseInfo:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    class HomeworkInfo:
        def __init__(self, name, grade, homework_id):
            self.name = name
            # self.url = "homeworkDemo.html"
            self.grade = grade
            self.homework_id = homework_id

    takings = TakingClass.query.filter_by(student_id=g.user.id).all()

    courses = []
    for taking in takings:
        course = Course.query.filter_by(id=taking.course_id).first()
        # print(course.name)
        courses.append(course)
        # print(type(courses))

    total0 = []
    for course in courses:
        # pass
        onecourse = CourseInfo(course.name, course.id)
        total0.append(onecourse)

    form = HomeworkForm()
    total = []
    if form.validate_on_submit():
        course_id = form.course_id.data
        homeworks = Homework.query.filter_by(course_id=course_id).all()

        for homework in homeworks:
            studentHomework = StudentHomework.query.filter_by(student_id=g.user.id).first()
            if studentHomework.homework_id == homework.id:
                total.append(HomeworkInfo(homework.name, studentHomework.grade, str(homework.id)))
    return render_template('homework.html', Total0=total0, Total=total, form=form)


@app.route('/ThomeworkDemo.html', methods=['GET', 'POST'])
@login_required
def ThomeworkDemo():
    form = CorrectHomeworkForm()
    try:
        homework_id = int(request.args.get('homework_id'))
    except:
        flash("Please specify homework_id")
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))

    class HomeworkInfo:
        def __init__(self, name, student_id, details, grade, url):
            self.student_name = name
            self.student_id = student_id
            self.details = details
            self.grade = grade
            self.url = url

    total = []
    studentHomeworks = StudentHomework.query.filter_by(homework_id=homework_id).all()
    homework = Homework.query.filter_by(id=homework_id).first()
    for studentHomework in studentHomeworks:
        student = User.query.filter_by(id=studentHomework.student_id).first()
        total.append(HomeworkInfo(student.name, student.id, homework.description, studentHomework.grade,
                                  studentHomework.homework_url))
    # total.append(HomeworkInfo())

    if form.validate_on_submit():
        try:
            student = User.query.filter_by(id=form.student_id.data).first()
            studentHomeworks = StudentHomework.query.filter_by(homework_id=homework_id).all()
            for studentHomework in studentHomeworks:
                if studentHomework.student_id == student.id:
                    studentHomework.grade = form.grade.data
                    db.session.commit()
                    print("marked!")
                    flash('The Homework is marked successfully!')
                    return redirect(url_for('ThomeworkDemo') + '?homework_id=' + str(homework_id))
        except Exception as e:
            flash(e, 'danger')

    return render_template('ThomeworkDemo.html', Total=total, form=form)


@app.route('/homeworkDemo.html', methods=['GET', 'POST'])
@login_required
def homeworkDemo():
    try:
        homework_id = int(request.args.get('homework_id'))
    except:
        flash("Please specify homework_id")
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))

    homework = Homework.query.filter_by(id=homework_id).first()

    class HomeworkInfo:
        def __init__(self, name, details, ddl):
            self.name = name
            self.details = details
            self.ddl = ddl

    form = UploadHomeworkForm()
    if form.validate_on_submit():
        try:
            filename = secure_filename(form.upload.data.filename)
            form.upload.data.save(os.path.join(app.config['UPLOADED_PHOTO_DEST'], filename))
            db.session.add(StudentHomework(homework_id, g.user.id, 'static/uploads/' + filename))
            db.session.commit()
            flash('The Homework is uploaded successfully!')
            return redirect(url_for('homeworkDemo') + '?homework_id=' + str(homework_id))
        except Exception as e:
            flash(e, 'danger')
    return render_template('homeworkDemo.html', homework=HomeworkInfo(homework.name, homework.description, "deadline:" + str(homework.deadline)), form=form)


@app.route('/info.html')
@login_required
def info():
    if g.user.user_type == 'teacher':
        return redirect('/TInfo.html')

    class ClassInfo:
        def __init__(self, name, details):
            self.name = name
            self.details = details

    class CourseInfo:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    Total = []
    takings = TakingClass.query.filter_by(student_id=g.user.id).all()
    for taking in takings:
        courses = Course.query.filter_by(id=taking.course_id).all()
        for course in courses:
            classInformations = ClassInformation.query.filter_by(course_id=course.id).all()
            for classInformation in classInformations:
                Total.append(ClassInfo(course.name, classInformation.content))
    return render_template('info.html', Total=Total)


@app.route('/media.html')
@login_required
def media():
    Total = []
    Total0 = []

    class MediaInfo:
        def __init__(self, url, img):
            self.id = url
            self.img = img

    class CourseInfo:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    takings = TakingClass.query.filter_by(student_id=g.user.id).all()
    for taking in takings:
        courses = Course.query.filter_by(id=taking.course_id).all()
        for course in courses:
            medias = Media.query.filter_by(course_id=course.id).all()
            for media in medias:
                Total.append(MediaInfo(media.url, course.course_url))

    return render_template('media.html', Total=Total)


@app.route('/mediaDemo.html')
@login_required
def mediaDemo():
    try:
        url = request.args.get('name')
    except:
        flash("error")
        if g.user.user_type == 'student':
            redirect(url_for(index))
        else:
            redirect(url_for(Tindex))

    class Info:
        def __init__(self, url):
            self.url = url

    return render_template('mediaDemo.html', row=Info(url))


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


@app.route('/TcourseDemo.html', methods=['GET', 'POST'])
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
            filename = secure_filename(form.upload.data.filename)
            form.upload.data.save(os.path.join(app.config['UPLOADED_PHOTO_DEST'], filename))

            csvFile = open(os.path.join(app.config['UPLOADED_PHOTO_DEST'], filename), "r")
            reader = csv.reader(csvFile)
            for item in reader:
                student_id = item[0].replace(' ', '')
                taking = TakingClass.query.filter_by(student_id=student_id).first()
                if taking is None:
                    user = User.query.filter_by(id=student_id).first()
                    if not user is None and user.user_type == 'student':
                        db.session.add(TakingClass(course_id, student_id))
                        print('add!')
                        db.session.commit()
            csvFile.close()

        except Exception as e:
            flash(e, 'danger')

    return render_template('TcourseDemo.html', courseInfo=CourseInfo(course.name, course.description), form=form)


@app.route('/Thomework.html', methods=['GET', 'POST'])
@login_required
def Thomework():
    total0 = []
    total = []

    form = AddHomeworkForm()
    if form.validate_on_submit():
        try:
            db.session.add(Homework(form.title.data, form.course_id.data, form.content.data, form.ddl.data))
            db.session.commit()
            flash('You have just added the homework successfully!', 'success')
        except Exception as e:
            flash(e, 'danger')

    class CourseInfo:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    class HomeworkInfo:
        def __init__(self, name, homework_id):
            self.name = name
            # self.url = "homeworkDemo.html"
            self.homework_id = homework_id

    courses = Course.query.filter_by(teacher_id=g.user.id).all()
    for course in courses:
        total0.append(CourseInfo(course.name, course.id))
        homeworks = Homework.query.filter_by(course_id=course.id).all()
        for homework in homeworks:
            total.append(HomeworkInfo(homework.name, str(homework.id)))

    return render_template('Thomework.html', Total0=total0, Total=total, form=form)


@app.route('/TInfo.html', methods=['GET', 'POST'])
@login_required
def Tinfo():
    form = Inform()
    if form.validate_on_submit():
        try:
            db.session.add(ClassInformation(form.course_id.data, form.content.data))
            db.session.commit()
            flash('You have just added the information successfully!', 'success')
        except Exception as e:
            flash(e, 'danger')

    class ClassInfo:
        def __init__(self, name, details):
            self.name = name
            self.details = details

    class CourseInfo:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    Total0 = []
    # courses = Course.query.filter_by(teacher_id=g.user.id).all()

    Total = []
    courses = Course.query.filter_by(teacher_id=g.user.id).all()
    for course in courses:
        Total0.append(CourseInfo(course.name, course.id))
        classInfomations = ClassInformation.query.filter_by(course_id=course.id).all()
        for classInfomation in classInfomations:
            Total.append(ClassInfo(course.name, classInfomation.content))
    return render_template('Tinfo.html', form=form, Total=Total, Total0=Total0)


@app.route('/Tmedia.html', methods=['GET', 'POST'])
@login_required
def Tmedia():
    form = UploadMediaForm()
    if form.validate_on_submit():
        try:
            filename = secure_filename(form.upload.data.filename)
            form.upload.data.save(os.path.join(app.config['UPLOADED_PHOTO_DEST'], filename))
            db.session.add(
                Media(form.name.data, form.course_id.data, 'static/uploads/' + filename))
            db.session.commit()
            flash('Upload successful!', 'success')
        except Exception as e:
            # flash ( 'login fail', 'primary' )
            flash(e, 'danger')

    Total = []
    Total0 = []

    class MediaInfo:
        def __init__(self, url, img):
            self.id = url
            self.img = img

    class CourseInfo:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    courses = Course.query.filter_by(teacher_id=g.user.id).all()
    for course in courses:
        Total0.append(CourseInfo(course.name, course.id))
        medias = Media.query.filter_by(course_id=course.id).all()
        for media in medias:
            Total.append(MediaInfo(media.url, course.course_url))

    return render_template('Tmedia.html', Total=Total, Total0=Total0, form=form)


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

    form = EditTeacherInfomationForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(id=g.user.id).first()
            user.name = form.name.data
            user.description = form.details.data
            user.email = form.email.data
            db.session.commit()
            print('OK!')
            redirect(url_for("teacherInfo"))
        except Exception as e:
            flash(e, 'danger')

    class TeachInfo:
        def __init__(self, name, details, email):
            self.name = name
            self.details = details
            self.email = email
    if g.user.user_type == 'student':
        return render_template('teacherInfo.html',
                               teachInfo=TeachInfo(teacher.name, teacher.description, teacher.email), form=form)
    else:
        return render_template('teacherInfo.html', teachInfo=TeachInfo(teacher.name, teacher.description, teacher.email),
                           teacher=True, form=form)


def test_login_logout(self):
    user = self.login('admin', 'default')
    assert 'You were logged in' in user.data
    user = self.logout()
    assert 'You were logged out' in user.data
    user = self.login('adminx', 'default')
    assert 'You should log in' in user.data


