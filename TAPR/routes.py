from flask import render_template, url_for, request, redirect, flash
from TAPR import app, db
from TAPR.models import *
from TAPR.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from TAPR.functions import *

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title = "Home")


@app.route("/login", methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.id.data).first()
        if user is not None and user.verify_password(form.password.data): 
            login_user(user)
            flash("Login Success!")
            next=request.args.get('next')
            return redirect(url_for('home'))
        else:
            flash("Email or Password incorrect.")
    else:
        flash_errors(form)
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash("You have successfully logged out!")
    next=request.args.get('next')
    return redirect(url_for('home'))


@app.route("/register", methods=['GET','POST'])
def register():
    next=request.args.get('next')
    if current_user.is_authenticated:
        flash("You've already logged in!")
        return redirect(next or url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(id=form.id.data,email=form.email.data,password=form.password.data,first_name=form.first_name.data,last_name=form.last_name.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Congratulations! Your registration has completed.")
        return redirect(url_for('home'))
    # else:
    #     flash_errors(form)
    return render_template('register.html', title='Register', form=form)


@app.route("/issues", methods=['GET','POST'])
def issues():
    form=IssueForm()
    return render_template('report_issues.html', title='Report Issues', form=form)



@app.route("/")
@app.route("/team_allocation", methods=['GET', 'POST'])
def team_allocation():
    form = TeamAllocation()
    if form.validate_on_submit():
        if len(Assessment.query.filter_by(id=form.assessment.data).first().student_team_list) > 0:
            flash("Teams already allocated!")
            return redirect(url_for('home'))
        assessment = Assessment.query.filter_by(id=form.assessment.data).first()
        students = User.query.filter_by(assessment_id=assessment.id).all()
        min_team_size = int(form.team_size.data)
        team_count = len(students) // min_team_size

        #Initialize teams
        for team_id in range(1, team_count+1):
            team = Team(id = team_id, assessment_id = assessment.id)
            db.session.add(team)
        teams = assessment.student_team_list

        #Allocate students to teams
        if form.native_speaker.data: addNativeSpeakers(teams, students)
        if form.prior_programming.data: addPriorProgrammers(teams, students)
        if form.prev_degree.data: addPreviousDegrees(teams, students, min_team_size)
        allocateStudents(teams, students, min_team_size) #Allocate any students not allocated

        db.session.commit()
        flash("Teams have been allocated!")
        return redirect(url_for('home'))
        
    return render_template('team_allocation.html', title = "Team Allocation", form=form)
