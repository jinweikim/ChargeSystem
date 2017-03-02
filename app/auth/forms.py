# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FloatField
from wtforms.validators import Required, Length, EqualTo, Regexp
from app.models import Discipline, Class, PaymentItem


# 用户登录表单
class LoginForm(Form):
    username = StringField(u'用户名', validators=[Required(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住')
    submit = SubmitField(u'登录')


# 更改密码表单
class ChangepasswordForm(Form):
    oldpassword = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'提交')


# 添加专业
class AddDisciplineForm(Form):
    number = StringField(u'专业代码', validators=[Length(0, 15), Required(), Regexp('[0-9]', 0, u'只能是0到9的数字')])
    name = StringField(u'专业名称', validators=[Length(0, 20), Required()])
    desc = TextAreaField(u'专业描述', validators=[Length(0, 100)])
    submit = SubmitField(u'提交')


# 添加班级
class AddClassForm(Form):
    name = StringField(u'班级名称', validators=[Length(0, 30), Required()])
    desc = TextAreaField(u'班级描述', validators=[Length(0, 100)])
    dis = SelectField(u'所属专业', coerce=str, validators=[Required(), Length(max=15)])
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(AddClassForm, self).__init__(*args, **kwargs)
        self.dis.choices = [(c.dis_number, c.dis_name) for c in Discipline.query.order_by(Discipline.dis_number).all()]


# 添加学生
class AddStudentForm(Form):
    number = StringField(u'学号', validators=[Length(0, 20), Required(), Regexp('[0-9]', 0, u'只能是0到9的数字')])
    name = StringField(u'姓名', validators=[Length(0, 20), Required()])
    sex = SelectField(u'性别', coerce=str, validators=[Length(0, 5), Required()])
    sart = SelectField(u'入学年份', coerce=str)
    destitute = SelectField(u'贫困', coerce=str)
    class_name = SelectField(u'所属班级', coerce=str)
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        self.sex.choices = [('Man', 'Man'), ('Woman', 'Woman')]
        self.sart.choices = [('2015', '2015'), ('2016', '2016'), ('2017', '2017')]
        self.destitute.choices = [('False', 'No'), ('True', 'Yes')]
        self.class_name.choices = [(str(c.id), c.class_name) for c in Class.query.order_by(Class.id).all()]


# 设置缴费表单
class PaymentItemForm(Form):
    dis = SelectField(u'专业', validators=[Required()])
    pay_year = SelectField(u'缴费年度', validators=[Required()])
    tuition_fee = StringField(u'学费')
    mis_fee = StringField(u'杂费')
    accom_fee = StringField(u'住宿费')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(PaymentItemForm, self).__init__(*args, **kwargs)
        self.dis.choices = [(c.dis_number, c.dis_name) for c in Discipline.query.order_by(Discipline.dis_number).all()]
        self.pay_year.choices = [('2015', '2015'), ('2016', '2016'), ('2017', '2017')]
        if self.dis.choices and self.pay_year.choices:
            choice_dis_number = self.dis.choices[0][0]
            choice_pay_year = self.pay_year.choices[0][0]
            pay_item = PaymentItem.query.filter_by(belong_dis=choice_dis_number, pay_year=choice_pay_year).first()


# 查询表单一
class QueryForm_1(Form):
    level = SelectField(u"按届级查询")
    submit = SubmitField(u'查询')

    def __init__(self, *args, **kwargs):
        super(QueryForm_1, self).__init__(*args, **kwargs)
        self.level.choices = [('2015', '2015'), ('2016', '2016'), ('2017', '2017')]


# 查询表单二
class QueryForm_2(Form):
    level_1 = SelectField(u"按班级查询")
    submit = SubmitField(u'查询')

    def __init__(self, *args, **kwargs):
        super(QueryForm_2, self).__init__(*args, **kwargs)
        self.level_1.choices = [(c.id, c.class_name) for c in Class.query.order_by(Class.id).all()]
