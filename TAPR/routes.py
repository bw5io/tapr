from flask import render_template, url_for, request
from TAPR import app, db
from blog.models import User, Issue, Team, Assessment, ContributionPercentage, PeerContributionForm

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')