from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin



app = Flask(__name__)   
app.config['SECRET_KEY']='2ea381c499e2df1774a2387309e4304579e3184bc143e629'
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://tapr:cN0I28nru5bYWt9Q@srv1.bw5.in:3306/tapr'
# app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'
# Admin User: 1 Password: Test1234    Student User: 1001-1098
# phpMyAdmin URL: http://srv1.bw5.in/phpmyadmin
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from TAPR import routes
from TAPR import models

from TAPR.views import AdminView
from TAPR.models import *


# admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
# admin.add_view(AdminView(User, db.session)) 
# admin.add_view(AdminView(Team, db.session)) 
# admin.add_view(AdminView(Issue, db.session))
# admin.add_view(AdminView(IssueStudentInvolved, db.session))
# admin.add_view(AdminView(Assessment, db.session))
# admin.add_view(AdminView(BandWeighting, db.session))
# admin.add_view(AdminView(ContributionForm, db.session))
# admin.add_view(AdminView(ContributionQuestion, db.session))
# admin.add_view(AdminView(ContributionFormAnswers, db.session))
# admin.add_view(AdminView(TeamMarkPercentage, db.session))

