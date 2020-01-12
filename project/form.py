from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    email = SubmitField('Email', validators=[ DataRequired(), Email()] )
    password = StringField('Password', validators=[DataRequired()])
    confirm_password = SubmitField('Confirm Password', validators=[DataRequired(), EqualTo('password') ])
    submit = SubmitField('Sign up')
    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("That email is taken. Please choose a new one")