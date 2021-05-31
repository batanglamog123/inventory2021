from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime

class User(db.Model, UserMixin):
    # username, number, email, role, activated
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(255), default="default.png")
    name = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    number = db.Column(db.Integer, unique=True)
    role = db.Column(db.String(150), default="User")
    activated = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    items = db.relationship('Item')
    feedbacks = db.relationship('Feedback', backref='user')
    issues = db.relationship('Issue', backref='user')
    logs = db.relationship('Log', backref='user')

class Item(db.Model):
    # name, model, brand, serial_number, category, type, department, remarks(not required), image, status, pr_number
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    model = db.Column(db.String(150))
    brand = db.Column(db.String(150))
    serial_number = db.Column(db.String(150))
    category = db.Column(db.String(150))
    item_type = db.Column(db.String(150))
    department = db.Column(db.String(150))
    remarks = db.Column(db.String(150), default="none")
    image = db.Column(db.String(255))
    status = db.Column(db.String(150))
    pr_number = db.Column(db.Integer)
    isApprove = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    specs = db.relationship('Spec')
    operators = db.relationship('Operator')
    adminNotifs = db.relationship('AdminNotification')
    itemNotifs = db.relationship('ItemNotification')
    itemApproval = db.relationship('ItemApproval')

class Spec(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String(150))
    gpu = db.Column(db.String(150))
    ram = db.Column(db.String(150))
    odd = db.Column(db.String(150))
    avr_ups = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

class Operator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.String(150))
    purpose = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

class ItemApproval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    model = db.Column(db.String(150))
    brand = db.Column(db.String(150))
    serial_number = db.Column(db.String(150))
    category = db.Column(db.String(150))
    item_type = db.Column(db.String(150))
    department = db.Column(db.String(150))
    remarks = db.Column(db.String(150), default="none")
    image = db.Column(db.String(255))
    status = db.Column(db.String(150))
    pr_number = db.Column(db.Integer)
    action = db.Column(db.String(150), default="add")
    isApprove = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    spec_approval = db.relationship('SpecApproval')
    operator_approval = db.relationship('OperatorApproval')

class SpecApproval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpu = db.Column(db.String(150))
    gpu = db.Column(db.String(150))
    ram = db.Column(db.String(150))
    odd = db.Column(db.String(150))
    avr_ups = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    itemApproval_id = db.Column(db.Integer, db.ForeignKey("item_approval.id"))

class OperatorApproval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.String(150))
    purpose = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())
    itemApproval_id = db.Column(db.Integer, db.ForeignKey("item_approval.id"))

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now())

class AdminNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(150))
    read = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

class ItemNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(150))
    read = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text)
    rating = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    details = db.Column(db.Text)
    screen_shot = db.Column(db.String(255))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    severity = db.Column(db.String(150))
    description = db.Column(db.Text)
    date = db.Column(db.Date(), default=func.now())
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))