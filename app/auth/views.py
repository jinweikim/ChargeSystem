# coding=utf-8

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .forms import LoginForm, ChangepasswordForm, AddDisciplineForm, AddClassForm, \
    AddStudentForm, PaymentItemForm, QueryForm_1, QueryForm_2
from app import db
from app.decorators import admin_required
from app.models import User, Discipline, Class, Student, PaymentItem, StuPayment


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/change', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangepasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpassword.data):
            current_user.change(form.password.data)
            flash("change succeed")
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash(u"密码错误")
            return render_template('auth/change.html', form=form)

    return render_template('auth/change.html', form=form)


@auth.route('/add_discipline', methods=['GET', 'POST'])
@login_required
@admin_required
def add_discipline():
    form = AddDisciplineForm()
    if form.validate_on_submit():
        if Discipline.query.filter_by(dis_number=form.number.data).first() or \
                Discipline.query.filter_by(dis_name=form.name.data).first():
            flash(u"错误：专业已存在")
        else:
            discipline = Discipline(
                dis_number=form.number.data,
                dis_name=form.name.data,
                dis_desc=form.desc.data
            )
            db.session.add(discipline)
            db.session.commit()
            flash(u"添加成功")
        return redirect(url_for('auth.add_discipline'))

    return render_template('auth/add_discipline.html', form=form)


@auth.route('/add_class', methods=['GET', 'POST'])
@login_required
@admin_required
def add_class():
    form = AddClassForm()
    if form.validate_on_submit():
        if Class.query.filter_by(class_name=form.name.data).first():
            flash(u"错误：班级已存在")
        else:
            _class = Class(
                class_name=form.name.data,
                class_desc=form.desc.data,
                belong_dis=form.dis.data
            )
            db.session.add(_class)
            db.session.commit()
            flash(u"添加成功")
        return redirect(url_for('auth.add_class'))

    return render_template('auth/add_class.html', form=form)


@auth.route('/add_student', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    form = AddStudentForm()
    if form.validate_on_submit():
        if Student.query.filter_by(stu_number=form.number.data).first():
            flash(u"错误：学生已存在")
        else:
            student = Student(
                stu_number=form.number.data,
                stu_name=form.name.data,
                sex=form.sex.data,
                start_year=form.sart.data,
                destitute=form.destitute.data,
                belong_class=form.class_name.data
            )
            db.session.add(student)

            # 添加学生后，增加一个与之对应的用户，以供学生进行登录
            user = User(
                username=form.number.data,
                password='111111',
                role_id=2
            )
            db.session.add(user)
            db.session.commit()

            student_info = Student.query.filter_by(stu_number=form.number.data).first()
            if student_info:
                # 设置该学生的缴费项目
                pay = PaymentItem.query.filter_by(belong_dis=student_info.class_name.discipline.dis_number,
                                            pay_year=student_info.start_year).first()
                if pay:
                    print student_info.start_year
                    stu_pay = StuPayment(
                                pay_year=student_info.start_year,
                                tuition=pay.tuition_fee,
                                actual_tution=0,
                                mis=pay.mis_fee,
                                actual_mis=0,
                                accom=pay.accom_fee,
                                actual_accom=0,
                                total=pay.tuition_fee + pay.mis_fee + pay.accom_fee,
                                actual_total=0,
                                payment_item=pay.item_number,
                                stu_number=student_info.stu_number
                            )
                else:
                    stu_pay = StuPayment(
                                pay_year=student_info.start_year,
                                tuition=0,
                                actual_tution=0,
                                mis=0,
                                actual_mis=0,
                                accom=0,
                                actual_accom=0,
                                total=-1,
                                actual_total=0,
                                stu_number=student_info.stu_number
                            )
                db.session.add(stu_pay)
                db.session.commit()
            flash(u"添加成功")

        return redirect(url_for('auth.add_student'))

    return render_template('auth/add_student.html', form=form)


@auth.route('/set_payment', methods=['GET', 'POST'])
@login_required
@admin_required
def set_payment():
    """管理员进行谋专业缴费项目的修改"""
    form = PaymentItemForm()
    if request.method == 'POST':
        pay_item = PaymentItem.query.filter_by(belong_dis=form.dis.data, pay_year=int(form.pay_year.data)).first()
        if pay_item:
            pay_item.tuition_fee = form.tuition_fee.data
            pay_item.mis_fee = form.mis_fee.data
            pay_item.accom_fee = form.accom_fee.data
            db.session.commit()
            flash(u'修改成功')
        else:
            pay_item = PaymentItem(
                pay_year=form.pay_year.data,
                tuition_fee=form.tuition_fee.data,
                mis_fee=form.mis_fee.data,
                accom_fee=form.accom_fee.data,
                belong_dis=form.dis.data
            )
            db.session.add(pay_item)
            db.session.commit()
            flash(u'设置成功')
        pay_item = PaymentItem.query.filter_by(belong_dis=form.dis.data, pay_year=int(form.pay_year.data)).first()
        stu_pay = StuPayment.query.filter_by(pay_year=int(form.pay_year.data)).all()
        if stu_pay and pay_item:
            for c in stu_pay:
                if c.student.class_name.discipline.dis_number == pay_item.belong_dis:
                    c.tuition = pay_item.tuition_fee
                    c.mis = pay_item.mis_fee
                    c.accom = pay_item.accom_fee
                    c.total = pay_item.tuition_fee + pay_item.mis_fee + pay_item.accom_fee
                    c.payment_item = pay_item.item_number
                    db.session.commit()
        return redirect(url_for('auth.set_payment'))

    return render_template('auth/set_payment.html', form=form)


@auth.route('/query', methods=['GET'])
@login_required
@admin_required
def query():
    """查询缴费情况"""
    form1 = QueryForm_1()
    form2 = QueryForm_2()
    return render_template('auth/query.html', form1=form1, form2=form2)


@auth.route('/count_1', methods=['GET', 'POST'])
@login_required
@admin_required
def count_1():
    """汇总缴费情况"""
    level = request.form['level']
    stu_pay = StuPayment.query.filter_by(pay_year=level).all()
    return render_template('auth/count_1.html', stu_pay=stu_pay)


@auth.route('/count_2', methods=['GET', 'POST'])
@login_required
@admin_required
def count_2():
    level = request.form['level_1']
    stu_pay = StuPayment.query.filter_by().all()
    return render_template('auth/count_2.html', stu_pay=stu_pay, level=int(level))


@auth.route('/ajax_dis', methods=['GET', 'POST'])
@login_required
@admin_required
def ajax_dis():                  # 利用ajax技术实现页面局部的变化
    dis = request.args.get('dis', '0', type=str)
    pay_year = request.args.get('pay_year', '0', type=str)
    pay_item = PaymentItem.query.filter_by(belong_dis=dis, pay_year=pay_year).first()
    if pay_item:
        return jsonify(tuition_fee=pay_item.tuition_fee, mis_fee=pay_item.mis_fee, accom_fee=pay_item.accom_fee)
    return jsonify(tuition_fee="0", mis_fee="0", accom_fee="0")   # 传递json数据


@auth.route('/ajax_year', methods=['GET', 'POST'])
@login_required
@admin_required
def ajax_year():
    dis = request.args.get('dis', '0', type=str)
    pay_year = request.args.get('pay_year', '0', type=str)
    pay_item = PaymentItem.query.filter_by(belong_dis=dis, pay_year=pay_year).first()
    if pay_item:
        return jsonify(tuition_fee=pay_item.tuition_fee, mis_fee=pay_item.mis_fee, accom_fee=pay_item.accom_fee)
    return jsonify(tuition_fee="0", mis_fee="0", accom_fee="0")

