from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class FeedbackForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired()])
    content = TextAreaField('内容', validators=[DataRequired()])
    submit = SubmitField('发送')
