from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms import DateField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User


class AssessmentForm(FlaskForm):
    module_code = StringField('Module Code', validators=[DataRequired()])
    title = StringField('Assessment Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d',validators=[DataRequired()])
    submit = SubmitField('Create Assessment')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password', message='passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered')
        

class EditProfileForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    new_password = PasswordField('New Password (optional)')
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Save Changes')

    def __init__(self, obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._obj = obj

    def validate_username(self, username):
        if self._obj and username.data != self._obj.username:
            existing_user = User.query.filter_by(username=username.data).first()
            if existing_user:
                raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if self._obj and email.data != self._obj.email:
            existing_user = User.query.filter_by(email=email.data).first()
            if existing_user:
                raise ValidationError('This email is already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')