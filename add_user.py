from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from forms import Login, SearchBookForm, ChangePasswordForm, EditInfoForm, SearchStudentForm, NewStoreForm, StoreForm, BorrowForm
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
import time, datetime

from sqlalchemy.orm import sessionmaker
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manager = Manager(app)

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(6), primary_key=True)
    admin_name = db.Column(db.String(32))
    password = db.Column(db.String(24))
    right = db.Column(db.String(32))

    def __init__(self, admin_id, admin_name, password, right):
        self.admin_id = admin_id
        self.admin_name = admin_name
        self.password = password
        self.right = right

    def get_id(self):
        return self.admin_id

    def verify_password(self, password):
        if password == self.password:
            return True
        else:
            return False

    def __repr__(self):
        return '<Admin %r>' % self.admin_name

class PredictData(db.Model):
    __tablename__ = 'predict_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    f1 = db.Column(db.String(64))
    f2 = db.Column(db.String(64))
    f3 = db.Column(db.String(64))
    label = db.Column(db.String(64))
    def __init__(self,f1, f2, f3, label):
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.label = label
    def __repr__(self):
        return '<f1: %r f2: %r f3: %r label: %r>' % (self.f1,self.f2,self.f3,self.label)

# 创建新User对象:
new_user =Admin(admin_id='22222',admin_name='patient',password='12345',right='2')
db.session.add(new_user)
db.session.commit()

#
# stu = Admin.query.get(0)
# db.session.delete(stu)  # 删除
# db.session.commit()  # 提交事务

# stu = Admin.query.filter_by(admin_id='cloud', password='12345').first()

# sut = PredictData.query.all()
# print(sut)


# sut = PredictData.query.all()
# PredictData.query.delete()
# db.session.commit()

