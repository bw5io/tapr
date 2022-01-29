from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin



app = Flask(__name__)   
app.config['SECRET_KEY']=os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from TAPR import routes
from TAPR import models

from TAPR.views import AdminView
from TAPR.models import *
