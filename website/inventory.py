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

inventory = Blueprint('inventory', __name__)

images = UploadSet('images', IMAGES)

class MyForm(FlaskForm):
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Images only!')
    ])

@inventory.route('/')
@login_required
def inventory_home():
    items = Item.query.filter_by(isApprove=1).order_by(desc(Item.created_at)).all()
    #items = Item.query.all()
    return render_template("home.html", items=items)

@inventory.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    form = MyForm()
    dept = Department.query.all()
    if request.method == 'POST':
        filename = images.save(form.image.data)

        name = request.form.get('name')
        model = request.form.get('model')
        brand = request.form.get('brand')
        serial_number = request.form.get('serial_number')
        category = request.form.get('category')
        item_type = request.form.get('item_type')
        department = request.form.get('department')
        remarks = request.form.get('remarks')
        status = request.form.get('status')
        pr_number = request.form.get('pr_number')
        user_id = current_user.id

        item_new = Item(name=name, model=model, brand=brand, serial_number=serial_number, category=category, item_type=item_type, department=department, remarks=remarks, image=filename, status=status, pr_number=pr_number, user_id=user_id)
        db.session.add(item_new)
        db.session.commit()

        itemApprovalNew = ItemApproval(name=name, model=model, brand=brand, serial_number=serial_number, category=category, item_type=item_type, department=department, remarks=remarks, image=filename, status=status, pr_number=pr_number, user_id=user_id, item_id=item_new.id)
        db.session.add(itemApprovalNew)
        db.session.commit()

        log = Log(severity='Permission', description=current_user.name+' has requested to add an item - '+name, user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        if category == "Computers":
            cpu = request.form.get('cpu')
            gpu = request.form.get('gpu')
            ram = request.form.get('ram')
            odd = request.form.get('odd')
            avr_ups = request.form.get('avr_ups')

            spec_new = Spec(cpu=cpu, gpu=gpu, ram=ram, odd=odd, avr_ups=avr_ups, item_id=item_new.id)
            db.session.add(spec_new)
            db.session.commit()

            specApprovalNew = SpecApproval(cpu=cpu, gpu=gpu, ram=ram, odd=odd, avr_ups=avr_ups, itemApproval_id=itemApprovalNew.id)
            db.session.add(specApprovalNew)
            db.session.commit()

        if status == "In Use":
            person = request.form.get('person')
            purpose = request.form.get('purpose')
                
            operator_new = Operator(person=person, purpose=purpose, item_id=item_new.id)
            db.session.add(operator_new)
            db.session.commit()

            operatorApprovalNew = OperatorApproval(person=person, purpose=purpose, itemApproval_id=itemApprovalNew.id)
            db.session.add(operatorApprovalNew)
            db.session.commit()

        flash("Item creation is in process. Please wait for the admin's approval.", category='success')
        return redirect(url_for('inventory.inventory_home'))

    return render_template("new_item.html", form=form, depts=dept)

@inventory.route('/delete_item/<itemid>')
@login_required
def deleteItem(itemid):
    item_id = itemid

    item_approval = ItemApproval.query.filter_by(item_id=item_id).first()
    
    if item_approval:
        item_approval.action = "delete"
        item_approval.isApprove = 0
        item_approval.updated_at = func.now()
        db.session.commit()

        log = Log(severity='Permission', description=current_user.name+' has requested to delete an item', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()

        flash("Item deletion is in process. Please wait for the admin's approval.", category='success')
        return redirect(url_for('inventory.inventory_home'))
    else:
        flash("Item might be deleted.", category='error')
        return redirect(url_for('inventory.inventory_home'))

@inventory.route('/view_item/<itemid>')
@login_required
def view_item(itemid):
    item_id = itemid

    item = Item.query.get(item_id)
    if item:
        specs = Spec.query.filter_by(item_id=item_id).first()
        operator = Operator.query.filter_by(item_id=item_id).first()
        return render_template("view_item.html", item=item, specs=specs, operator=operator)
    else:
        flash('Item might be deleted', category='error')
        return redirect(url_for('inventory.inventory_home'))

@inventory.route('/edit_item/<itemid>',  methods=['GET', 'POST'])
@login_required
def edit_item(itemid):
    item_id = itemid
    item = Item.query.get(item_id)
    specs = Spec.query.filter_by(item_id=item_id).first()
    operator = Operator.query.filter_by(item_id=item_id).first()
    dept = Department.query.order_by(desc(Department.dept_name)).all()

    name = request.form.get('name')
    model = request.form.get('model')
    brand = request.form.get('brand')
    serial_number = request.form.get('serial_number')
    category = request.form.get('category')
    item_type = request.form.get('item_type')
    department = request.form.get('department')
    remarks = request.form.get('remarks')
    status = request.form.get('status')
    pr_number = request.form.get('pr_number')

    if request.method == 'POST':
        if item:
            item_approval = ItemApproval.query.filter_by(item_id=item_id).first()

            if item_approval:
                item_approval.name = name
                item_approval.model = model
                item_approval.brand = brand
                item_approval.serial_number = serial_number
                item_approval.category = category
                item_approval.item_type = item_type
                item_approval.department = department
                item_approval.remarks = remarks
                item_approval.status = status
                item_approval.pr_number = pr_number
                item_approval.action = "edit"
                item_approval.isApprove = 0
                item_approval.updated_at = func.now()
                db.session.commit()
            else:
                itemApprovalNew = ItemApproval(name=name, model=model, brand=brand, serial_number=serial_number, category=category, item_type=item_type, department=department, action="edit", remarks=remarks, status=status, pr_number=pr_number, user_id=current_user.id, item_id=item_id)
                db.session.add(itemApprovalNew)
                db.session.commit()

            log = Log(severity='Permission', description=current_user.name+' has requested to edit an item - '+name, user_id=current_user.id)
            db.session.add(log)
            db.session.commit()

            if category == "Computers":
                specs_approval = SpecApproval.query.filter_by(itemApproval_id=item_approval.id).first()
                cpu = request.form.get('cpu')
                gpu = request.form.get('gpu')
                ram = request.form.get('ram')
                odd = request.form.get('odd')
                avr_ups = request.form.get('avr_ups')

                if specs_approval:
                    specs_approval.cpu = cpu
                    specs_approval.gpu = gpu
                    specs_approval.ram = ram
                    specs_approval.odd = odd
                    specs_approval.avr_ups = avr_ups
                    db.session.commit()
                else:
                    spec_new = SpecApproval(cpu=cpu, gpu=gpu, ram=ram, odd=odd, avr_ups=avr_ups, itemApproval_id=item_approval.id)
                    db.session.add(spec_new)
                    db.session.commit()
                    
            if status == "In Use":
                operator_approval = SpecApproval.query.filter_by(itemApproval_id=item_approval.id).first()
                person = request.form.get('person')
                purpose = request.form.get('purpose')
                    
                if operator_approval:
                    operator_approval.person = person
                    operator_approval.purpose = purpose
                    db.session.commit()
                else:
                    operator_new = Operator(person=person, purpose=purpose, item_id=item_id, itemApproval_id=item_approval.id)
                    db.session.add(operator_new)
                    db.session.commit()

            flash('Item updated. Please wait for the admin to approve changes.', category='success')
            return redirect(url_for('inventory.inventory_home'))
        else:
            return redirect(url_for('inventory.inventory_home'))

    return render_template("edit_item.html", item=item, specs=specs, operator=operator, depts=dept)

@inventory.route('/edit_image/<itemid>',  methods=['GET', 'POST'])
@login_required
def edit_image(itemid):
    item_id = itemid
    item = Item.query.get(item_id)
    form = MyForm()
    if request.method == 'POST':
        if item:
            item_approval = ItemApproval.query.filter_by(item_id=item_id).first()
            filename = images.save(form.image.data)
            
            if item_approval:
                item_approval.image = filename
                item_approval.isApprove = 0
                item_approval.action = "edit image"
                item_approval.updated_at = func.now()
                db.session.commit()
            else:
                itemApprovalNew = ItemApproval(image=filename, isApprove=0, action="edit image", updated_at=func.now(), user_id=current_user.id, item_id=item_id)
                db.session.add(itemApprovalNew)
                db.session.commit()

            log = Log(severity='Permission', description=current_user.name+' has requested to edit the image of an item - ' + item.name, user_id=current_user.id)
            db.session.add(log)
            db.session.commit()

            flash('Image update is in process. Admin will make an approval with this.', category='success')
            return redirect(url_for('inventory.inventory_home'))
    return render_template("edit_image.html", item=item, form=form)

@inventory.route('/departments', methods=['GET', 'POST'])
@login_required
def departments():
    dept = Department.query.order_by(asc(Department.dept_name)).all()
    if request.method == 'POST':
        name = request.form.get('name')
        dept_new = Department(dept_name=name)
        db.session.add(dept_new)
        db.session.commit()
        #flash('Department/Unit Office added!', category='success')
        return redirect(url_for('inventory.departments'))
    return render_template("departments.html", depts=dept)

@inventory.route('admin_notif')
@login_required
def admin_notif():
    notifs = AdminNotification.query.order_by(desc(AdminNotification.date)).all()
    return render_template("admin_notif.html", notifs=notifs)

@inventory.route('view_admin_notif/<id>')
@login_required
def view_admin_notif(id):
    notif_id = id
    notif = AdminNotification.query.get(id)
    notif.read = 1
    db.session.commit()

    item = Item.query.get(notif.item_id)
    if item:
        specs = Spec.query.filter_by(item_id=notif.item_id).first()
        operator = Operator.query.filter_by(item_id=notif.item_id).first()
        return render_template("view_item.html", item=item, specs=specs, operator=operator)
    else:
        flash('Item might be deleted.', category='error')
        return redirect(url_for('inventory.admin_notif'))

@inventory.route('/admin_notif_count', methods=['GET'])
def admin_notif_count():
    count = AdminNotification.query.filter_by(read=0).count()
    return make_response(jsonify(count), 200)

@inventory.route('/item_notification')
def item_notification():
    notifs = ItemNotification.query.order_by(desc(ItemNotification.date)).all()
    return render_template("item_notification.html", notifs=notifs)

@inventory.route('/count_notif')
def count_notif():
    count = ItemNotification.query.filter_by(read=0).count()
    return make_response(jsonify(count), 200)

@inventory.route('/view_notif')
@login_required
def view_notif():
    notif_id = request.args.get('notif_id')
    item_id = request.args.get('item_id')

    notif = ItemNotification.query.get(notif_id)
    if notif:
        notif.read = 1
        db.session.commit()
        
        item = Item.query.get(item_id)

        if item:
            specs = Spec.query.filter_by(item_id=item_id).first()
            operator = Operator.query.filter_by(item_id=item_id).first()
            return render_template("view_item.html", item=item, specs=specs, operator=operator)
        else:
            flash('Item might be deleted', category='error')
            return redirect(url_for('inventory.item_notification'))

