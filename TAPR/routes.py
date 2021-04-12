from flask import render_template, url_for, request
from TAPR import app, db
from TAPR.models import *
from TAPR.forms import *

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/")
@app.route("/team-allocation")
def team_allocation():
    return render_template('team-allocation.html')
