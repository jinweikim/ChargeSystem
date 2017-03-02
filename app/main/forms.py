# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import Required, Length, Regexp, Email
from wtforms import ValidationError
from flask.ext.login import current_user
from app.models import Role, User


# 显示学生信息
class ShowForm(Form):
    stu_number = StringField(u'学号')
    stu_name = StringField(u'姓名')
    sex = StringField(u'性别')
    stat = StringField(u'入学年份')
    destitute = StringField(u'是否贫困')
    belong_class = StringField(u'班级')
    discipline = StringField(u'专业')


# 缴学费
class PaymentForm(Form):
    tuition = FloatField(u'应交学费')
    al_tuition = FloatField(u'已交学费')
    actual_tution = FloatField(u'学费')
    mis = FloatField(u'应交杂费')
    al_mis = FloatField(u'已交杂费')
    actual_mis = FloatField(u'杂费')
    accom = FloatField(u'应交住宿费')
    al_accom = FloatField(u'已交住宿费')
    actual_accom = FloatField(u'住宿费')
    submit = SubmitField(u'提交')