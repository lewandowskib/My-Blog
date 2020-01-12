from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[ DataRequired(), Email()] )
    password = StringField('Password', validators=[DataRequired()])
    confirm_password = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password') ])
    permission = SelectField('Permission',choices=[('user', 'User'), ('admin', 'Admin')])
    submit = SubmitField('Sign up')
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email is taken. Please choose a new one")

    def validate_username(self, username):
        username = User.query.filter_by(username=username.data).first()
        if email:
            raise ValidationError("That username is taken. Please choose a new one")