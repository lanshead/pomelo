from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class ReportTest1(FlaskForm):
    label1 = StringField('поле1', validators=[DataRequired()])
    label2 = StringField('поле2', validators=[DataRequired()])
    create = SubmitField('Создать задачу')
