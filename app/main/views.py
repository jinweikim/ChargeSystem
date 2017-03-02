# coding=utf-8

from flask import render_template, redirect, request, url_for, flash, abort
from flask_login import login_required, current_user
from . import main
from .forms import ShowForm, PaymentForm
from app import db
from app.models import Student, StuPayment


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template("index.html")


@main.route('/show_message/<username>')
@login_required
def show_message(username):
    """查看个人信息"""
    form = ShowForm()
    user = Student.query.filter_by(stu_number=username).first()
    if user is None:
        abort(404)

    form.stu_number.data = user.stu_number
    form.stu_name.data = user.stu_name
    form.sex.data = user.sex
    form.stat.data = user.start_year
    form.destitute.data = user.destitute
    form.belong_class.data = user.class_name.class_name
    form.discipline.data = user.class_name.discipline.dis_name
    return render_template('user.html', form=form)


@main.route('/stu_payment', methods=['GET', 'POST'])
@login_required
def stu_payment():
    """缴费"""
    form = PaymentForm()
    stu_pay = StuPayment.query.filter_by(stu_number=current_user.username).first()
    if request.method == 'POST':
        stu_pay.actual_tution = stu_pay.actual_tution + form.actual_tution.data
        stu_pay.actual_mis = stu_pay.actual_mis + form.actual_mis.data
        stu_pay.actual_accom = stu_pay.actual_accom + form.actual_accom.data
        stu_pay.actual_total = stu_pay.actual_total + form.actual_tution.data + form.actual_mis.data + form.actual_accom.data
        db.session.commit()
        flash(u"缴费成功")
        return redirect(url_for('main.stu_payment'))

    if stu_pay and stu_pay.total >= 0:
        form.tuition.data = stu_pay.tuition
        form.al_tuition.data = stu_pay.actual_tution

        form.mis.data = stu_pay.mis
        form.al_mis.data = stu_pay.actual_mis

        form.accom.data = stu_pay.accom
        form.al_accom.data = stu_pay.actual_accom
    else:
        flash(u"尚未开始收费")
        return redirect(url_for('main.index'))
    return render_template('stu_payment.html', form=form)


