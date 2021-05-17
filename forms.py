from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length


class Login(FlaskForm):
    account = StringField(u'账号', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u'登录')



class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'原密码', validators=[DataRequired()])
    password = PasswordField(u'新密码', validators=[DataRequired(), EqualTo('password2', message=u'两次密码必须一致！')])
    password2 = PasswordField(u'确认新密码', validators=[DataRequired()])
    submit = SubmitField(u'确认修改')


class EditInfoForm(FlaskForm):
    name = StringField(u'用户名', validators=[Length(1, 32)])
    submit = SubmitField(u'提交')

class FeatureForm(FlaskForm):
    f1 = StringField(u'feature1', validators=[DataRequired()])
    f2 = StringField(u'feature2', validators=[DataRequired()])
    f3 = StringField(u'feature3', validators=[DataRequired()])
    label = StringField(u'label', validators=[DataRequired()])
    submit = SubmitField(u'预测')


class HarrisScoreForm(FlaskForm):
    subtime = StringField(u'subtime', validators=[DataRequired()])
    pain = StringField(u'pain', validators=[DataRequired()])
    func = StringField(u'func', validators=[DataRequired()])
    rng = StringField(u'rng', validators=[DataRequired()])
    score = StringField(u'score', validators=[DataRequired()])
    submit = SubmitField(u'提交')





class AdviceForm(FlaskForm):
    patient_id = StringField(u'patient_id', validators=[DataRequired()])
    advice = StringField(u'advice', validators=[DataRequired()])

    submit = SubmitField(u'提交')
