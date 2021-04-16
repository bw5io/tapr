from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)   
app.config['SECRET_KEY']='2ea381c499e2df1774a2387309e4304579e3184bc143e629'
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://tapr:cN0I28nru5bYWt9Q@srv1.bw5.in:3306/tapr'
# app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///test.db'
# Admin User: Test1001 Password: Test1234

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from TAPR import routes
from TAPR import models

