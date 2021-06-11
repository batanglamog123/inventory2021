from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from . import db
from .models import Item, Spec, Operator, Department, AdminNotification, ItemNotification, ItemApproval, SpecApproval, OperatorApproval, User, Log
import json
from flask_wtf import FlaskForm
from wtforms import FileField
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask_wtf.file import FileField, FileAllowed, FileRequired
from sqlalchemy import desc, asc
from sqlalchemy.sql import func

approval = Blueprint('item_approval', __name__)

images = UploadSet('images', IMAGES)

class MyForm(FlaskForm):
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
])

@approval.route('/item_approval')
@login_required
def item_approval():
    items = ItemApproval.query.filter_by(isApprove=0).order_by(desc(ItemApproval.created_at)).all()
    return render_template("item_approval.html", items=items)

@approval.route('/view_item_approval_add/<id>')
@login_required
def view_item_approval_add(id):
    a_id = id
    item = ItemApproval.query.get(a_id)
    if item:
        user = User.query.filter_by(id=item.user_id).first()
        specs = SpecApproval.query.filter_by(itemApproval_id=a_id).first()
        operator = OperatorApproval.query.filter_by(itemApproval_id=a_id).first()
        return render_template("view_item_approval_add.html", item=item, specs=specs, operator=operator, user=user)
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('inventory.item_approval'))
    
@approval.route('/view_item_approval_edit/<id>')
@login_required
def view_item_approval_edit(id):
    a_id = id
    itemApproval = ItemApproval.query.get(a_id)
    specsApproval = SpecApproval.query.filter_by(itemApproval_id=a_id).first()
    operatorApproval = OperatorApproval.query.filter_by(itemApproval_id=a_id).first()
    if itemApproval:
        item = Item.query.get(itemApproval.item_id)
        user = User.query.filter_by(id=itemApproval.user_id).first()
        specs = Spec.query.filter_by(item_id=item.id).first()
        operator = Operator.query.filter_by(item_id=item.id).first()
        return render_template("view_item_approval_edit.html", item=item, itemApproval=itemApproval, specs=specs, operator=operator, specsApproval=specsApproval, operatorApproval=operatorApproval, user=user)
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('inventory.item_approval'))

@approval.route('/view_item_approval_image/<id>')
@login_required
def view_item_approval_image(id):
    a_id = id
    itemApproval = ItemApproval.query.get(a_id)
    specsApproval = SpecApproval.query.filter_by(itemApproval_id=a_id).first()
    operatorApproval = OperatorApproval.query.filter_by(itemApproval_id=a_id).first()
    if itemApproval:
        item = Item.query.get(itemApproval.item_id)
        user = User.query.filter_by(id=itemApproval.user_id).first()
        return render_template("view_item_approval_image.html", item=item, itemApproval=itemApproval, user=user)
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('inventory.item_approval'))

@approval.route('/approve_edit')
@login_required
def approve_edit():
    itemId = request.args.get('id')
    approvalId = request.args.get('a_id')

    item = Item.query.get(itemId)
    item_approval = ItemApproval.query.get(approvalId)

    if item:
        item.name = item_approval.name
        item.model = item_approval.model
        item.brand = item_approval.brand
        item.serial_number = item_approval.serial_number
        item.category = item_approval.category
        item.item_type = item_approval.item_type
        item.department = item_approval.department
        item.remarks = item_approval.remarks
        item.status = item_approval.status
        item.pr_number = item_approval.pr_number
        item.isApprove = 1
        item.updated_at = func.now()
        db.session.commit()

        item_approval.isApprove = 1
        db.session.commit()

        notif = ItemNotification(content=item.name+" was updated", item_id=itemId)
        db.session.add(notif)
        db.session.commit()

        log = Log(severity='Permission', description=current_user.name+' approved item update', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        if item_approval.category == "Computers":
            specs = Spec.query.filter_by(item_id=itemId).first()
            specs_approval = SpecApproval.query.filter_by(itemApproval_id=approvalId).first()
            if specs:
                specs.cpu = specs_approval.cpu
                specs.gpu = specs_approval.gpu
                specs.ram = specs_approval.ram
                specs.odd = specs_approval.odd
                specs.avr_ups = specs_approval.avr_ups
                db.session.commit()
            else:
                spec_new = Spec(cpu=specs_approval.cpu, gpu=specs_approval.gpu, ram=specs_approval.ram, odd=specs_approval.odd, avr_ups=specs_approval.avr_ups, item_id=itemId)
                db.session.add(spec_new)
                db.session.commit()
        
        if item_approval.status == "In Use":
            operator = Operator.query.filter_by(item_id=itemId).first()
            operator_approval = SpecApproval.query.filter_by(itemApproval_id=approvalId).first()
                    
            if operator_approval:
                operator.person = operator_approval.person
                operator.purpose = operator_approval.purpose
                db.session.commit()
            else:
                operator_new = Operator(person=person, purpose=purpose, item_id=item_id)
                db.session.add(operator_new)
                db.session.commit()

        flash("Item updates approved!", category='success')
        return redirect(url_for('item_approval.item_approval'))
    else :
        flash("Item might be deleted", category='error')
        return redirect(url_for('item_approval.item_approval'))

@approval.route('/view_item_approval_delete/<id>')
@login_required
def view_item_approval_delete(id):
    a_id = id
    itemApproval = ItemApproval.query.get(a_id)
    specsApproval = SpecApproval.query.filter_by(itemApproval_id=a_id).first()
    operatorApproval = OperatorApproval.query.filter_by(itemApproval_id=a_id).first()
    if itemApproval:
        item = Item.query.get(itemApproval.item_id)
        user = User.query.filter_by(id=itemApproval.user_id).first()
        specs = Spec.query.filter_by(item_id=item.id).first()
        operator = Operator.query.filter_by(item_id=item.id).first()
        return render_template("view_item_approval_delete.html", item=item, itemApproval=itemApproval, specs=specs, operator=operator, specsApproval=specsApproval, operatorApproval=operatorApproval, user=user)
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('inventory.item_approval'))

@approval.route('/item_approval_approve/<id>', methods=['GET', 'POST'])
@login_required
def item_approval_approve(id):
    item_id = id
    item = Item.query.get(item_id)
    item_approval = ItemApproval.query.filter_by(item_id=item_id).first()

    if item:
        item.isApprove = 1
        db.session.commit()
        item_approval.isApprove = 1
        db.session.commit()

        notif = ItemNotification(content="New item added - "+item.name, item_id=item_id)
        db.session.add(notif)
        db.session.commit()

        log = Log(severity='Permission', description=current_user.name+' approved item creation', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash('Item creation approved!', category='success')
        return redirect(url_for('item_approval.item_approval'))
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('item_approval.item_approval'))

@approval.route('/item_disapproval_approve/<id>', methods=['GET', 'POST'])
@login_required
def item_disapproval_approve(id):
    item_id = id
    item = Item.query.get(item_id)
    item_approval = ItemApproval.query.filter_by(item_id=item_id).first()

    if item:
        db.session.delete(item)
        db.session.commit()

        db.session.delete(item_approval)
        db.session.commit()

        log = Log(severity='Permission', description=current_user.name+' disapproved item creation', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash('Item creation disapproved!', category='success')
        return redirect(url_for('item_approval.item_approval'))
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('item_approval.item_approval'))

@approval.route('/delete_approval')
@login_required
def delete_approval():
    itemId = request.args.get('id')
    approvalId = request.args.get('a_id')

    item = Item.query.get(itemId)
    item_approval = ItemApproval.query.get(approvalId)

    notif = ItemNotification(content=item.name+" was deleted", item_id=itemId)
    db.session.add(notif)
    db.session.commit()

    log = Log(severity='Permission', description=current_user.name+' approved item deletion', user_id=current_user.id)
    db.session.add(log)
    db.session.commit()

    db.session.delete(item)
    db.session.commit()

    db.session.delete(item_approval)
    db.session.commit()

    flash('Item deletion approved! Item was deleted.', category='success')
    return redirect(url_for('item_approval.item_approval'))

@approval.route('/image_approval')
@login_required
def image_approval():
    itemId = request.args.get('id')
    approvalId = request.args.get('a_id')

    item = Item.query.get(itemId)
    item_approval = ItemApproval.query.get(approvalId)

    if item:
        item.image = item_approval.image
        item.isApprove = 1
        item.updated_at = func.now()
        db.session.commit()

        item_approval.isApprove = 1
        db.session.commit()

        notif = ItemNotification(content=item.name+" - image updated", item_id=itemId)
        db.session.add(notif)
        db.session.commit()

        log = Log(severity='Permission', description=current_user.name+' approved item image update', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash("Item updates approved!", category='success')
        return redirect(url_for('item_approval.item_approval'))
    else :
        flash("Item might be deleted", category='error')
        return redirect(url_for('item_approval.item_approval'))

@approval.route('/approval_count')
@login_required
def approval_count():
    count = ItemApproval.query.filter_by(isApprove=0).count()
    return make_response(jsonify(count), 200)