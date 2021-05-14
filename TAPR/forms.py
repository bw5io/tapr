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
    team_size = RadioField(choices=[(5, 'Groups of 5-6 members'), (6, 'Groups of 6-7 members')])
    prior_programming = BooleanField('Member with prior programming experience')
    native_speaker = BooleanField('English native speaker')
    prev_degree = BooleanField('BA, BSc, BEng and LLB graduate')
    submit = SubmitField('Submit')

class IssueForm(FlaskForm):
    issue_type = RadioField('Please select which issue you are experiencing:', choices=[(1, 'Unresponsive team members'), (2, 'Issues of significant disagreement'), (3, 'Bullying or harassment within the team'), (4, 'Other')])
    members_involved = RadioField('Which team members are involved in your issue:', choices=[])
    attempts_resolve = BooleanField('If possible, have you made substantial efforts to resolve this problem within the team, allowing time for change/improvements to take place? See [link to advice on team working]')
    issue_description = StringField('Please provide relevant details about your issue in the box below. Include details about when the problem began, how you have attempted to solve it and any suggestions you have going forward. All comments will be kept private but please be as professional as possible.', validators=[DataRequired(), Length(min=50, max=1500)],render_kw={"placeholder":"Describe your issue here."})
    submit = SubmitField('Report Issue')

class LaunchMarkingForm(FlaskForm):
    assessment_id = IntegerField('Assessment ID')
    submit = SubmitField('Submit')

class QuestionnaireForm(FlaskForm):
    native_speaker=BooleanField("Are you a Native Speaker")
    coding_experience=BooleanField("Do you have Coding Experience")
    degree_program = RadioField('Which is your previous Degree Program: ', choices=[("BA"), ("BSc"), ("LLM"), ("BEng")])
    submit = SubmitField("Form Complete")


class EvaluationForm(FlaskForm):
    student_evaluated = SelectField('Choose a group member you want to evaluate : ', choices=[])
    question = RadioField('Performance in teamwork : ', choices=[(5, 'Excellent'), (4, 'Good'), (3, 'Average'), (2, 'Below Average'), (1,'No Contribution')])
    #question_two = RadioField('Second Question:', choices=[(5, 'Excellent'), (4, 'Good'), (3, 'Average'), (2, 'Below Average'), (1,'No Contribution')])
    submit = SubmitField("Submit Evaluation")
class TeamReset(FlaskForm):
    assessment = IntegerField('Assessment ID')
    submit = SubmitField('Submit')
