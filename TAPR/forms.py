from flask_wtf import *
from wtforms import *
from wtforms.validators import *
from TAPR.models import *

class RegistrationForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired(), Length(min=3, max=15, message="Username should be 3 to 15 characters long.")],render_kw={"placeholder":"3 to 15 characters long"})
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',validators=[DataRequired(),Regexp('^.{6,8}$',message='Password must be between 6 and 8 characters long.')])
    confirm_password=PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password',message="Two Passwords are not the same.")])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    submit=SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(message='Username already exist. Please choose a different one.')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(message='Email already in use. Please choose a different one.')


class LoginForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TeamAllocation(FlaskForm):
    assessment = IntegerField('Assessment ID')
    team_size = RadioField('Specify team size range by choosing one of the following:', choices=[(5, '5-6 students per group'), (6, '6-7 students per group')])
    prior_programming = BooleanField('Where possible include at least one student with prior programming experience for each team:')
    native_speaker = BooleanField('Where possible include at least one English native speaker for each team:')
    prev_degree = BooleanField('Where possible include at least one BA, BSc, BEng and LLB graduate for each team:')
    submit = SubmitField('Submit')


