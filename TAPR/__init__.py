from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

app = Flask(__name__)   
app.config['SECRET_KEY']='2ea381c499e2df1774a2387309e4304579e3184bc143e629'
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from TAPR import routes
from TAPR import models.*

from blog.views import AdminView
admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session)) 
admin.add_view(AdminView(Post, db.session)) 
admin.add_view(AdminView(Comment, db.session))