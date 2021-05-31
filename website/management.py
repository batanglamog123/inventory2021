from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, Response, current_app
from . import db
from .models import User, Feedback, Issue, Log
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import desc, asc, func
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
from fpdf import FPDF
import os

management = Blueprint('management', __name__)

@management.route('/accounts')
@login_required
def accounts():
    users = User.query.order_by(desc(User.created_at)).all()
    return render_template("accounts.html", users=users)

@management.route('/new_account', methods=['GET', 'POST'])
#@login_required
def new_account():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        number = request.form.get('number')
        email = request.form.get('email')

        user_email = User.query.filter_by(email=email).first()
        user_username = User.query.filter_by(username=username).first()
        user_number = User.query.filter_by(number=number).first()

        if user_username:
            flash('Username already exist!', category='error')
        elif user_email:
            flash('Email already exist!', category='error')
        elif user_number:
            flash('Contact number is already taken!', category='error')
        elif len(username) < 6:
            flash('Username is too short', category='error')
        else:
            new_account = User(name=name, username=username, number=number, password=generate_password_hash("inventory", method='sha256'), email=email)
            db.session.add(new_account)
            db.session.commit()

            log = Log(severity='Permission', description='Created a user - '+name, user_id=current_user.id)
            db.session.add(log)
            db.session.commit()

            flash('Account created!', category='success')
            return redirect(url_for('management.accounts'))

    return render_template("new_account.html")

@management.route('/view_account/<accountId>')
@login_required
def view_account(accountId):
    user = User.query.get(accountId)
    return render_template("view_account.html", user=user)

@management.route('/reset_password/<accountId>')
@login_required
def reset_pass(accountId):
    user_id = accountId
    password = generate_password_hash("inventory", method='sha256')

    user = User.query.get(user_id)

    if user:
        user.password = password
        db.session.commit()

        log = Log(severity='Permission', description='Password reset a user', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash('Password reset success!', category='success')
        return redirect(url_for('management.accounts'))

@management.route('/client_feedbacks')
@login_required
def feedbacks():
    #feedbacks = Feedback.query.order_by(desc(Feedback.date)).all()
    feedbacks = Feedback.query.join(User).filter(Feedback.user_id==User.id).order_by(desc(Feedback.date)).all()
    return render_template("client_feedbacks.html", feedbacks=feedbacks)

@management.route('/client_issues')
@login_required
def client_issues():
    issues = Issue.query.join(User).filter(Issue.user_id==User.id).order_by(desc(Issue.date)).all()
    return render_template("client_issues.html", issues=issues)

@management.route('/view_issue/<id>')
@login_required
def view_issue(id):
    issue = Issue.query.join(User).filter(Issue.user_id==User.id, Issue.id==id).first()
    return render_template("view_issue.html", issue=issue)

@management.route('/system_logs')
@login_required
def system_logs():
    logs = Log.query.join(User).filter(Log.user_id==User.id).order_by(desc(Log.timestamp)).all()
    #log_date = Log.query.with_entities(Log.date).distinct()
    log_date = Log.query.all()

    return render_template("system_logs.html", logs=logs, log_date=log_date)

@management.route('/download_logs', methods=['POST'])
@login_required
def download_logs():
    if request.method == 'POST':
        log_date = request.form.get('date')

        logs = Log.query.filter(func.date(Log.date)==log_date).all()
        #logs = Log.query.filter_by(date=date).join(User).filter(Log.user_id==User.id).order_by(desc(Log.timestamp)).all()

        return render_template("preview_log.html", logs=logs, date=log_date)

@management.route('/delete_account/<id>')
@login_required
def delete_account(id):
    user_id = id

    user = User.query.get(user_id)

    db.session.delete(user)
    db.session.commit()

    log = Log(severity='Permission', description='Deleted a user - '+user.name, user_id=current_user.id)
    db.session.add(log)
    db.session.commit()

    flash('User deleted!', category='success')
    return redirect(url_for('management.accounts'))

@management.route('/user_activate/<id>')
@login_required
def user_activate(id):
    user_id = id

    user = User.query.get(user_id)

    user.activated = 1
    db.session.commit()

    log = Log(severity='Permission', description='Activated a user - '+user.name, user_id=current_user.id)
    db.session.add(log)
    db.session.commit()

    flash('User activated!', category='success')
    return redirect(url_for('management.accounts'))

@management.route('/user_deactivate/<id>')
@login_required
def user_deactivate(id):
    user_id = id

    user = User.query.get(user_id)

    user.activated = 0
    db.session.commit()

    log = Log(severity='Permission', description='Deactivated a user - '+user.name, user_id=current_user.id)
    db.session.add(log)
    db.session.commit()

    flash('User deactivated!', category='success')
    return redirect(url_for('management.accounts'))

@management.route('/send_feedback', methods=['POST'])
@login_required
def send_feedback():
    if request.method == 'POST':
        details = request.form.get('details')
        rating = request.form.get('rating')

        feedback = Feedback(details=details, rating=rating, user_id=current_user.id)
        db.session.add(feedback)
        db.session.commit()

        log = Log(severity='Info', description='Sent feedback', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash('Feedback sent!', category='success')
        return redirect(url_for('inventory.inventory_home'))

@management.route('/send_issue', methods=['POST'])
@login_required
def send_issue():
    if request.method == 'POST':
        f = request.files['file']
        details = request.form.get('details')
        title = request.form.get('title')

        if f:
            #f.save(secure_filename(f.filename))
            f.save(os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            issue = Issue(details=details, title=title, screen_shot=f.filename, user_id=current_user.id)
            db.session.add(issue)
            db.session.commit()
        else:
            issue = Issue(details=details, title=title, user_id=current_user.id)
            db.session.add(issue)
            db.session.commit()
        
        log = Log(severity='Info', description='Reported an issue', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash('Issue sent!', category='success')
        return redirect(url_for('inventory.inventory_home'))
    
