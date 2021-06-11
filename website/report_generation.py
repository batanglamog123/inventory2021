from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, Response, current_app
from flask_login import login_required, current_user
from . import db
from .models import Item, Department
from sqlalchemy import desc, asc, func

report_generation = Blueprint('report_generation', __name__)

@report_generation.route('/generate_dept')
@login_required
def generate_by_dept():
    depts = Department.query.all()
    items = Item.query.all()
    return render_template("generate_dept.html", items=items, depts=depts)
