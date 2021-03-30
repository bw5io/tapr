from datetime import datetime
from blog import db
from blog import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Table to store User Information
class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    is_student = db.Column(db.Boolean, nullable=False, default=False)
    native_speaker = db.Column(db.Boolean)
    coding_experience = db.Column(db.Boolean)
    previous_degree = db.Column(db.String(20))
    team_mark_percentage = db.relationship("TeamMarkPercentage")

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash,password)

# Table to store Teams
class Team(db.Model):
    __tablename__ = "Team"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('Assessment.id'), nullable=False)
    team_members = db.relationship("User")
    contribution_forms = db.relationship("ContributionForm")
    issues = db.Column(db.Integer, db.ForeignKey('Issue.id'))

# Tables to store Issues
class Issue(db.Model):
    __tablename__ = "Issue"
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    students_involved = db.relationship('IssueStudentInvolved')
    issue_type = db.relationship("IssueType")
    complaint = db.Column(db.String(1000))
    team = db.relationship("Team")

class IssueType(db.Model):
    __tablename__ = "IssueType"
    id = db.Column(db.Integer, primary_key=True)
    issue_description = db.Column(db.String(120))
    issue_id = db.Column(db.Integer, db.ForeignKey('Issue.id'), nullable=False)


class IssueStudentInvolved():
    __tablename__ = "IssueStudentInvolved"
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('Issue.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

# Table to store Assessment
class Assessment(db.Model):
    __tablename__ = "Assessment"
    id = db.Column(db.Integer, primary_key=True)
    module_info = db.Column(db.String(60), nullable=False)
    student_list = db.relationship("User")
    module_team_list = db.relationship("Team")
    contribution_questions = db.relationship("ContributionQuestion")
    band_weighting = db.relationship("BandWeighting")

class BandWeighting():
    __tablename__ = "BandWeighting"
    id = db.Column(db.Integer, primary_key=True)
    assessment = db.Column(db.Integer, db.ForeignKey('Assessment.id'), nullable = False)
    contribution_avg = db.Column(db.Integer, nullable=False)
    teamMark_percentage = db.Column(db.Integer, nullable=False)

class ContributionQuestion(db.Model): 
    __tablename__ = "ContributionQuestion"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('Assessment.id'), nullable=False)
    question = db.Column(db.String(120), nullable=False) 
    

# Tables for Peer Contribution Form
class ContributionForm(db.Model):
    __tablename__ = "ContributionForm"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("Team.id"))
    student_submitter = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    student_evaluated = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    contribution_answers = db.relationship("ContributionFormAnswers")
    

class ContributionFormAnswers(db.Model):
    __tablename__ = "ContributionFormAnswers"
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey("ContributionForm.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("ContributionQuestion.id"), nullable=False)
    answer = db.Column(db.Integer)

# Tables for Contribution Percentage
class TeamMarkPercentage(db.Model):
    __tablename__ = "TeamMarkPercentage"
    id = db.Column(db.Integer, primary_key=True)
    team_mark_percentage = db.Column(db.Integer, nullable=False)
    student = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
     

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# class TeamMember(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     studentID = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
#     teamID = db.Column(db.Integer, db.ForeignKey('Team.id'), nullable=False)

