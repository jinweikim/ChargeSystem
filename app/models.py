# coding=utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    permissions = db.Column(db.Integer, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    @property
    def password(self):
        raise AttributeError('paaword is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def change(self, newpassword):
        self.password = newpassword
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username


class Discipline(db.Model):
    __tablename__ = 'discipline_info'
    dis_number = db.Column(db.String(15), primary_key=True)
    dis_name = db.Column(db.String(20), nullable=False, unique=True)
    dis_desc = db.Column(db.String(100))
    class_name = db.relationship('Class', backref='discipline', lazy='dynamic')


class Class(db.Model):
    __tablename__ = 'class_info'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(20), nullable=False)
    class_desc = db.Column(db.String(100))
    belong_dis = db.Column(db.String(15), db.ForeignKey('discipline_info.dis_number'))
    student = db.relationship('Student', backref='class_name', lazy='dynamic')


class Student(db.Model):
    __tablename__ = 'student_info'
    stu_number = db.Column(db.String(20), primary_key=True)
    stu_name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(5), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    destitute = db.Column(db.Boolean, default=False)
    belong_class = db.Column(db.Integer, db.ForeignKey('class_info.id'))
    stu_pay = db.relationship('StuPayment', backref='student', lazy='dynamic')


class PaymentItem(db.Model):
    __tablename__ = 'payment_item'
    item_number = db.Column(db.Integer, primary_key=True)
    pay_year = db.Column(db.Integer)
    tuition_fee = db.Column(db.Float)
    mis_fee = db.Column(db.Float)
    accom_fee = db.Column(db.Float)
    belong_dis = db.Column(db.String(15), db.ForeignKey('discipline_info.dis_number'))


class StuPayment(db.Model):
    __tablename__ = 'stu_payment'
    id = db.Column(db.Integer, primary_key=True)
    pay_year = db.Column(db.Integer, nullable=False)
    tuition = db.Column(db.Float, nullable=False)
    actual_tution = db.Column(db.Float)
    mis = db.Column(db.Float, nullable=False)
    actual_mis = db.Column(db.Float)
    accom = db.Column(db.Float, nullable=False)
    actual_accom = db.Column(db.Float)
    total = db.Column(db.Float, nullable=False)
    actual_total = db.Column(db.Float)
    remark = db.Column(db.String(50))
    payment_item = db.Column(db.Integer, db.ForeignKey('payment_item.item_number'))
    stu_number = db.Column(db.String(20), db.ForeignKey('student_info.stu_number'))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
