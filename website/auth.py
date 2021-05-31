from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from . import db
from .models import User, Log
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import desc, asc
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired

auth = Blueprint('auth', __name__)

images = UploadSet('images', IMAGES)

class MyForm(FlaskForm):
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)

                log = Log(severity='Info', description=current_user.name+' has logged in', user_id=current_user.id)
                db.session.add(log)
                db.session.commit()

                return redirect(url_for('inventory.inventory_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')

    return render_template("login.html")

@auth.route('/logout')
def logout():
    log = Log(severity='Info', description=current_user.name+' has logged out', user_id=current_user.id)
    db.session.add(log)
    db.session.commit()
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template("profile.html")

@auth.route('/role_checker')
@login_required
def role_checker():
    return jsonify(current_user.role)

@auth.route('/settings')
@login_required
def settings():
    form = MyForm()
    return render_template("settings.html", form=form, account=current_user)

@auth.route('/account_profile', methods=['POST'])
@login_required
def account_profile():
    if request.method == 'POST':
        id = current_user.id
        name = request.form.get('name')
        username = request.form.get('username')
        number = request.form.get('number')
        email = request.form.get('email')

        user_email = User.query.filter(User.email==email, User.id!=id).all()
        user_username = User.query.filter(User.username==username, User.id!=id).all()
        user_number = User.query.filter(User.number==number, User.id!=id).all()
        user = User.query.get(id)

        if user_username:
            flash('Username already exist!', category='error')
            return redirect(url_for('auth.settings'))
        elif user_email:
            flash('Email already exist!', category='error')
            return redirect(url_for('auth.settings'))
        elif user_number:
            flash('Contact number is already taken!', category='error')
            return redirect(url_for('auth.settings'))
        elif len(username) < 6:
            flash('Username is too short', category='error')
            return redirect(url_for('auth.settings'))
        else:
            user.name = name
            user.username = username
            user.number = number
            user.email = email
            db.session.commit()

            log = Log(severity='Info', description='Patched own account', user_id=current_user.id)
            db.session.add(log)
            db.session.commit()

            flash('Account profile updated!', category='success')
            return redirect(url_for('auth.settings'))

@auth.route('/profile_image', methods=['POST'])
@login_required
def profile_image():
    form = MyForm()
    if request.method == 'POST':
        filename = images.save(form.image.data)
        current_user.image = filename
        db.session.commit()

        log = Log(severity='Info', description='Patched own profile image', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash('Image updated!', category='success')
        return redirect(url_for('auth.settings'))

@auth.route('/remove_profile_image')
@login_required
def remove_profile_image():
    current_user.image = "default.png"
    db.session.commit()

    log = Log(severity='Info', description='Set profile image to default', user_id=current_user.id)
    db.session.add(log)
    db.session.commit()

    flash('Image removed!', category='success')
    return redirect(url_for('auth.settings'))

@auth.route('/update_password', methods=['POST'])
@login_required
def update_password():
    if request.method == 'POST':
        current = request.form.get('current')
        new = request.form.get('new')
        confirm = request.form.get('confirm')

        if check_password_hash(current_user.password, current):
            if new == confirm:
                if len(new) < 8:
                    flash('Your password must be at least 8 or more characters in length!', category='error')
                    return redirect(url_for('auth.settings'))
                else:
                    current_user.password = generate_password_hash(new, method='sha256')
                    db.session.commit()

                    log = Log(severity='Info', description='Set new password', user_id=current_user.id)
                    db.session.add(log)
                    db.session.commit()

                    flash('Password reset success!', category='success')
                    return redirect(url_for('auth.settings'))
            else:
                flash('Password does not match', category='error')
                return redirect(url_for('auth.settings'))
        else:
            flash('Incorrect password', category='error')
            return redirect(url_for('auth.settings'))