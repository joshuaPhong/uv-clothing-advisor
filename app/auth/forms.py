from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField(
          'Username', validators=[DataRequired(), Length(
                min=4, max=20,
                message='Username must be between 4 and 20 characters'
          )]
    )
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
          'Password', validators=[DataRequired(), Length(
                min=6,
                message='Password must be at least 6 characters long'
          )]
    )
    password2 = PasswordField(
          'Repeat Password', validators=[DataRequired(), EqualTo(
             'password', message='Passwords must match'
             )]
    )
    submit = SubmitField('Register')
