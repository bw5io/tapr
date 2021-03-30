from datetime import datetime
from blog import db
from blog import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    uniqueid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    is_student = db.Column(db.Boolean, nullable=False, default=False)
    
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

class Issue(db.Model):
    pass


class Team(db.Model):
    pass

class Assessment(db.Model):
    pass

class ContributionPercentage(db.Model):
    pass

class PeerContributionForm(db.Model):
    pass



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
