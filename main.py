from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from forms import Login, SearchBookForm, ChangePasswordForm, EditInfoForm, SearchStudentForm, NewStoreForm, StoreForm, BorrowForm,FeatureForm, HarrisScoreForm
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
import time, datetime
from functools import cmp_to_key

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manager = Manager(app)

app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)


def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Book=Book)


manager.add_command("shell", Shell(make_context=make_shell_context))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'
login_manager.login_message = u"请先登录。"


# method2
def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d




class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(6), primary_key=True)
    admin_name = db.Column(db.String(32))
    password = db.Column(db.String(24))
    right = db.Column(db.String(32))
    harris_table =  db.relationship('HarrisScoreData',backref='user')

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

class HarrisScoreData(db.Model):
    __tablename__ = 'harrisscore_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subtime = db.Column(db.String(64))
    pain = db.Column(db.String(64))
    func = db.Column(db.String(64))
    rng = db.Column(db.String(64))
    score = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'))
    def __init__(self,subtime, pain, func, rng, score,user_id):
        self.subtime = subtime
        self.pain = pain
        self.func = func
        self.rng = rng
        self.score = score
        self.user_id = user_id
    def __repr__(self):
        return '<time: %r pain: %r function: %r range: %r score: %r>\n' % (self.subtime,self.pain,self.func,self.rng,self.score)

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))


@app.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = Admin.query.filter_by(admin_id=form.account.data, password=form.password.data).first()

        if user is None:
            flash('账号或密码错误！')
            return redirect(url_for('login'))
        else:
            login_user(user)
            session['admin_id'] = user.admin_id
            session['name'] = user.admin_name
            session['right'] = user.right
            if  session['right']=='1':
                return  redirect(url_for('index_doctor'))
            else:
                return redirect(url_for('index_patient'))

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经登出！')
    return redirect(url_for('login'))


@app.route('/user/<id>')
@login_required
def user_info(id):
    user = Admin.query.filter_by(admin_id=id).first()
    if user.right == '1':
        return render_template('doctor_user-info.html', user=user, name=session.get('name'))
    else:
        return render_template('patient_user-info.html', user=user, name=session.get('name'))


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.password2.data != form.password.data:
        flash(u'两次密码不一致！')
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'已成功修改密码！')
            if current_user.right == '1':
                return redirect(url_for('index_doctor'))
            else:
                return redirect(url_for('index_patient'))
        else:
            flash(u'原密码输入错误，修改失败！')
    if current_user.right == '1':
        return render_template("doctor_change-password.html", form=form)
    else:
        return render_template("patient_change-password.html", form=form)



@app.route('/change_info', methods=['GET', 'POST'])
@login_required
def change_info():
    form = EditInfoForm()
    if form.validate_on_submit():
        current_user.admin_name = form.name.data
        db.session.add(current_user)
        flash(u'已成功修改个人信息！')
        return redirect(url_for('user_info', id=current_user.admin_id))
    form.name.data = current_user.admin_name
    id = current_user.admin_id
    right = current_user.right
    return render_template('change-info.html', form=form, id=id, right=right)


#----------------------------------------- doctor model ---------------------------------------------------


@app.route('/index_doctor')
@login_required
def index_doctor():
    if current_user.right!='1':
        return render_template('patient_error.html')
    return render_template('index_doctor.html', name=session.get('name'))

@app.route('/index_patient')
@login_required
def index_patient():
    return render_template('index_patient.html', name=session.get('name'))

@app.route("/predict",methods=["GET", "POST"])
@login_required
def predict():
    if current_user.right!='1':
        return render_template('patient_error.html')
    form = FeatureForm()
    return render_template("predict.html",form = form)


@app.route("/predict_model", methods=["GET", "POST"])
@login_required
def predict_model():
    if current_user.right!='1':
        return render_template('patient_error.html')
    form = FeatureForm()

    label = form.f1.data+form.f2.data+form.f3.data
    new_data = PredictData(f1 = form.f1.data,f2 = form.f2.data,f3= form.f3.data, label = label)
    db.session.add(new_data)
    db.session.commit()
    form.label.data = label
    return render_template("predict.html",form = form)



@app.route("/oldmsg", methods=["GET", "POST"])
@login_required
def oldmsg():
    if current_user.right!='1':
        return render_template('patient_error.html')
    return render_template('oldmsg.html')

@app.route("/oldmsg/table/", methods=["GET", "POST"])
@login_required
def oldmsg_table():
    if current_user.right!='1':
        return render_template('patient_error.html')
    print("ok")
    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))
    print(page,limit)
    data = PredictData.query.all()
    tmp = []
    start = (page-1)*limit
    end = min(len(data),start+limit)
    data = data[start:end]
    for i in data:
        tmp.append(row2dict(i))
    #return "nihao"
    return jsonify({'code':0,'data':tmp})

@app.route("/delitem", methods=["POST"])
@login_required
def delitem():
    del_id = int(request.form['id'])
    print(del_id)
    try:
        tmp = PredictData.query.get(del_id)
        db.session.delete(tmp)  # 删除
        db.session.commit()  # 提交事务'
        return jsonify({"success": 200, "msg": "delete success"})
    except Exception as e:
        return jsonify({"error": 1001, "msg": "delete fail"})

@app.route("/changeitem", methods=["POST"])
@login_required
def changeitem():
    id = int(request.form['id'])
    f1 = request.form['f1']
    f2 = request.form['f2']
    f3 = request.form['f3']
    label = request.form['label']
    try:
        tmp = PredictData.query.filter(PredictData.id == id).first()
        tmp.f1 = f1
        tmp.f2 = f2
        tmp.f3 = f3
        tmp.label = label
        db.session.commit()  # 提交事务'
        return jsonify({"success": 200, "msg": "change success"})
    except Exception as e:
        return jsonify({"error": 1001, "msg": "change fail"})

#------------------------------------------- patient model ----------------------------------------------------

@app.route("/harris_date", methods=["GET","POST"])
@login_required
def harris_date():
    if current_user.right!='2':
        return render_template('doctor_error.html')
    return render_template('harris_date.html')

@app.route("/harris_table", methods=["GET","POST"])
@login_required
def harris_table():
    if current_user.right!='2':
        return render_template('doctor_error.html')
    print(request.args["time"])
    form = HarrisScoreForm()
    return render_template('harris_table.html',time = request.args["time"],form = form)

@app.route("/record_harris", methods=["POST"])
@login_required
def record_harris():
    if current_user.right!='2':
        return render_template('doctor_error.html')
    form = HarrisScoreForm()
    new_data = HarrisScoreData(subtime=form.subtime.data,pain=form.pain.data,func=form.func.data,rng=form.rng.data,score=form.score.data,user_id = current_user.admin_id)
    db.session.add(new_data)
    db.session.commit()
    return render_template('harris_date.html')



def data_compare(it1,it2):
    tmp1 = tmp2 = ''
    for i in it1.split('-'):
        tmp1 += i
    for i in it2.split('-'):
        tmp2 += i
    tmp1 = int(tmp1)
    tmp2 = int(tmp2)
    if tmp1<tmp2:
        return -1
    elif tmp1>tmp2:
        return 1
    else:
        return 0

def sortedDict(adict):
    keys = list(adict.keys())
    keys.sort(key = cmp_to_key(data_compare))
    value = []
    for key in keys:
        value.append(adict[key])
    return keys,value

@app.route("/harris_echarts")
@login_required
def harris_echarts():
    if current_user.right!='2':
        return render_template('doctor_error.html')

    print(current_user.harris_table)
    tmp = current_user.harris_table
    data = {}
    for i in tmp:
        data[i.subtime] = i.score

    keys,values = sortedDict(data)
    print(keys,values)
    #return redirect(url_for('index_patient'))

    return render_template('harris_echarts.html', keys = keys,values = values)















if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
