from flask import render_template, url_for, request, redirect, flash
from flask.templating import render_template_string
from sqlalchemy.sql.elements import Null
from TAPR import app, db
from TAPR.models import *
from TAPR.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from TAPR.functions import *
from random import choice
from statistics import mean


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

@app.route("/team_reset", methods=['GET', 'POST'])
def team_reset():
    form = TeamReset()
    if form.validate_on_submit():
        if Assessment.query.filter_by(id=form.assessment.data).first() == None:
            flash("Assessment ID not recognized. Please make sure the assessment has been created.")
            return redirect(url_for('team_reset'))
        if form.assessment.data == 1:
            return redirect(url_for('reset_user'))
    return render_template('team_reset.html', title = "Team Reset", form=form)

@app.route("/team_allocation", methods=['GET', 'POST'])
def team_allocation():
    form = TeamAllocation()
    if form.validate_on_submit():
        if Assessment.query.filter_by(id=form.assessment.data).first() == None:
            flash("Assessment ID not recognized. Please make sure the assessment has been created.")
            return redirect(url_for('team_allocation'))
        if len(Assessment.query.filter_by(id=form.assessment.data).first().student_team_list) > 0:
            flash("Teams have already been allocated.")
            return redirect(url_for('home'))

        #Add team composition to database
        team_composition = TeamComposition(id = 1, team_size=form.team_size.data, native_speaker=form.native_speaker.data, coding_experience=form.prior_programming.data, previous_degree=form.prev_degree.data)
        db.session.add(team_composition)

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
        flash("Teams have successfully been allocated.")
        return redirect(url_for('home'))

    return render_template('team_allocation.html', title = "Team Allocation", form=form)

@app.route("/team_lists")
def team_lists():
    assessment = Assessment.query.filter_by(id=1).first()
    team_composition = TeamComposition.query.filter_by(id=1).first()
    return render_template('team_lists.html', title='Team List', assessment=assessment, team_composition=team_composition)

@app.route("/team_lists/downloads")
def team_lists_download():
    assessment = User.query.filter_by(assessment_id=1).all()
    assessment.sort(key=returnTeamID)
    return render_csv("Team ID, Surname, First Name, Student ID, Email, Native Speaker, Coding Experience, Previous Degree",assessment,"team_list.csv")

@app.route("/team/<int:team_id>")
def team(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template('team.html', title='Team', team=team)

@app.route("/team/<int:team_id>/download")
def team_download(team_id):
    team = Team.query.get_or_404(team_id)
    return render_csv("Team ID, Surname, First Name, Student ID, Email, Native Speaker, Coding Experience, Previous Degree",team.team_members,"team_list_"+str(team_id)+".csv")

@app.route('/questionnaire', methods=['GET', 'POST'])
def questions():
    form = QuestionnaireForm()
    if form.validate_on_submit():
        # form data
        user = User.query.filter_by(id=current_user.id).first()
        user.native_speaker=form.native_speaker.data
        user.coding_experience=form.coding_experience.data
        user.previous_degree=form.degree_program.data
        db.session.commit()
        # success message
        flash("Questionnaire submitted successfully!")
        # on success, then redirect to home screen.
        return redirect('/home')
    return render_template("allocation_questionnaire.html", title="Questionnaire", form=form)


@app.route('/questionnaire_results', methods=['GET', 'POST'])
def questionnaire_results():
    return render_template("questionnaire_results.html", title="Results")

@app.route('/calculate_mark')
def calculate_mark():
    return render_template("team_allocation.html", title = "")

@app.route('/calculate_mark_run')
def calculate_mark_run():
    teams = Team.query.filter_by(assessment_id=1).all()
    for team in teams:
        mark = {}
        for form in team.contribution_forms:
            student = form.student_evaluated
            if student not in mark: mark[student]=0
            for answer in form.contribution_answers:
                mark[student]+=answer.answer
        team_average = mean(mark.values())
        for i,j in mark.items():
            newTMP = TeamMarkPercentage(student=i,team_mark_percentage=int(round(100*j/team_average,0)))
            db.session.add(newTMP)
            db.session.commit()
            print(newTMP)
        print(team.id, mark, mean(mark.values()))

    return "Done"

# Customized Scripts

@app.route("/utility/batch_register")
def batch_register():
    assignment = Assessment(id=1,module_info="Who Cares?")
    db.session.add(assignment)
    db.session.commit()
    for i in range(1001,1099,1):
        print(i)
        user=User(id=i,email="test"+str(i)+"@test.in",password="Test1234",first_name="Test",last_name="Bot"+str(i),assessment_id=1,is_student=1)
        db.session.add(user)
        db.session.commit()
    flash("Batch registration completed.")
    return redirect(url_for('home'))

@app.route("/utility/reset_user")
def reset_user():
    for i in range(1001,1099,1):
        user= User.query.filter_by(id=i).first()
        user.team_id=None
        user.is_student=1
        user.native_speaker=choice(seq=[True,False])
        user.coding_experience=choice(seq=[True,False])
        user.previous_degree=choice(seq=["BA", "BSc", "LLB", "BEng"])
        print(user)
        db.session.commit()
    db.session.query(IssueStudentInvolved).delete()
    db.session.commit()
    db.session.query(TeamMarkPercentage).delete()
    db.session.commit()
    db.session.query(ContributionFormAnswers).delete()
    db.session.commit()
    db.session.query(ContributionForm).delete()
    db.session.commit()
    db.session.query(Issue).delete()
    db.session.commit()
    db.session.query(Team).delete()
    db.session.commit()
    db.session.query(TeamComposition).delete()
    db.session.commit()
    flash("Reset complete.")
    return redirect(url_for('home'))

@app.route("/utility/batch_marking")
def batch_marking():
    for i in range(1001,1099,1):
        user = User.query.filter_by(id=i).first()
        team = Team.query.filter_by(id=user.team_id).first()
        questionnaire = ContributionQuestion.query.filter_by(assessment_id=1)
        for marked_marker in team.team_members:
            conForm = ContributionForm(team_id = team.id, student_submitter = user.id, student_evaluated = marked_marker.id)
            db.session.add(conForm)
            db.session.commit()
            conForm = ContributionForm.query.filter_by(student_submitter = user.id, student_evaluated = marked_marker.id).first()
            for question in questionnaire:
                quest = ContributionFormAnswers(form_id = conForm.id, question_id = question.id, answer = choice(seq=[5,4,3,2,1]))
                db.session.add(quest)
                db.session.commit()
            print(conForm)
    return "Done"
