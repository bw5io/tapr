from datetime import datetime
from TAPR import db
from TAPR import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Table to store User Information
class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('Team.id'))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    password_hash = db.Column(db.String(128))
    is_student = db.Column(db.Boolean, nullable=False, default=False)
    native_speaker = db.Column(db.Boolean)   
    coding_experience = db.Column(db.Boolean)
    previous_degree = db.Column(db.String(20))  #BA, BSc, LLM, BEng
    team_mark_percentage = db.relationship("TeamMarkPercentage")
    issues_submitted = db.relationship("Issue",back_populates="applicant")
    assessment_id = db.Column(db.Integer, db.ForeignKey('Assessment.id')) 


    def __repr__(self):
        return f"{self.team_id}, {self.last_name}, {self.first_name}, {self.id}, {self.email}, {self.native_speaker}, {self.coding_experience}, {self.previous_degree}" #change this in main

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
    issues = db.relationship("Issue")

# Tables to store Issues
class Issue(db.Model):
    __tablename__ = "Issue"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('Team.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    applicant = db.relationship("User",back_populates="issues_submitted")
    students_involved = db.relationship('IssueStudentInvolved')
    issue_type = db.Column(db.String(100), nullable=False)
    attempts_resolve = db.Column(db.Boolean, nullable=False, default=False)
    issue_description = db.Column(db.String(1000))
    

class IssueStudentInvolved(db.Model):
    __tablename__ = "IssueStudentInvolved"
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('Issue.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    students_involved = db.relationship('User')

# Table to store Assessment
class Assessment(db.Model):
    __tablename__ = "Assessment"
    id = db.Column(db.Integer, primary_key=True)
    module_info = db.Column(db.String(60), nullable=False) 
    student_list = db.relationship("User")
    student_team_list = db.relationship("Team")
    contribution_form_questions = db.relationship("ContributionQuestion")
    band_weighting = db.relationship("BandWeighting")
    is_calculated = db.Column(db.Boolean, nullable=False, default=False)
    # issue_type = db.relationship("IssueType")

class BandWeighting(db.Model):
    __tablename__ = "BandWeighting"
    id = db.Column(db.Integer, primary_key=True)
    assessment = db.Column(db.Integer, db.ForeignKey('Assessment.id'), nullable = False)
    contribution_avg = db.Column(db.Integer, nullable=False)
    teamMark_percentage = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return f"{self.id}, {self.contribution_avg}, {self.teamMark_percentage}"

    
# Tables for Peer Contribution Form
class ContributionForm(db.Model):
    __tablename__ = "ContributionForm"
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("Team.id"))
    student_submitter = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    student_evaluated = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=False)
    contribution_answers = db.relationship("ContributionFormAnswers")
    
    def __repr__(self):
        return f"{self.id}, {self.team_id}, {self.student_evaluated}, {self.student_submitter}"


class ContributionQuestion(db.Model): 
    __tablename__ = "ContributionQuestion"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('Assessment.id'), nullable=False)
    question = db.Column(db.String(120), nullable=False)


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
    assessment_id = db.Column(db.Integer, db.ForeignKey("Assessment.id"), nullable=False)

    def __repr__(self):
        return f"{self.id}, {self.team_mark_percentage}, {self.student}"


class TeamComposition(db.Model):
    __tablename__ = "TeamComposition"
    id = db.Column(db.Integer, primary_key=True)
    team_size = db.Column(db.Integer)
    native_speaker = db.Column(db.Boolean)
    coding_experience = db.Column(db.Boolean)
    previous_degree = db.Column(db.Boolean)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# class TeamMember(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     studentID = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
#     teamID = db.Column(db.Integer, db.ForeignKey('Team.id'), nullable=False)

# class IssueType(db.Model):
#     __tablename__ = "IssueType"
#     id = db.Column(db.Integer, primary_key=True)
#     issue_description = db.Column(db.String(120))
#     # Assessment_id = db.Column(db.Integer, db.ForeignKey('Issue.id'), nullable=False)

