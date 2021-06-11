from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, Response, current_app
from flask_login import login_required, current_user
from . import db
from .models import Item
from sqlalchemy import desc, asc, func

report_generation = Blueprint('report_generation', __name__)

@report_generation.route('/report_gen')
@login_required
def report_gen():
    return render_template("report_generation.html")

@report_generation.route('/generate_dept')
@login_required
def generate_by_dept():
    items = Item.query.all()
    return render_template("generate_dept.html", items=items)
