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
    member = User.query.filter_by(team_id=current_user.team_id).all()
    member_list = []
    for i in member:
        member_list.append((i.id, i.first_name+" "+i.last_name))
    form.members_involved.choices=member_list
    if form.validate_on_submit():
        issue=Issue(team_id = current_user.team_id, applicant_id =current_user.id,issue_type=form.issue_type.data,attempts_resolve=form.attempts_resolve.data,issue_description=form.issue_description.data)
        db.session.add(issue)
        db.session.commit()
        reported_user = IssueStudentInvolved(issue_id = issue.id, student_id = form.members_involved.data)
        print(issue.id)
        db.session.add(reported_user)
        db.session.commit()
        flash("Your issue has been recorded and someone will get back to you in 7 working days.")
        return redirect(url_for('home'))
    return render_template('report_issues.html', title='Report Issues', form=form)

@app.route("/view-issues", methods=['GET','POST'])
def view_issues():
    issues=Issue.query.order_by(Issue.team_id.desc()).all()
    return render_template('view_issues.html', title='View Reported Issues', issues=issues)
    

@app.route("/team_reset", methods=['GET', 'POST'])
def team_reset():
    form = TeamReset()
    if form.validate_on_submit():
        if Assessment.query.filter_by(id=form.assessment.data).first() == None:
            flash("Assessment ID not recognized. Please make sure the assessment has been created.")
            return redirect(url_for('team_reset'))
        if form.assessment.data == 1:
            return redirect(url_for('reset_teams'))
    return render_template('team_reset.html', title = "Team Reset", form=form)

@app.route("/team_allocation", methods=['GET', 'POST'])
def team_allocation():
    form = TeamAllocation()
    if form.validate_on_submit():
        if len(Assessment.query.filter_by(id=form.assessment.data).first().student_team_list) > 0:
            flash("Teams already allocated!")
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
        flash("Teams have been allocated!")
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
def questionnaire():
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



@app.route('/calculate_mark')
def calculate_mark():
    assessment = Assessment.query.all()
    return render_template("calculate_mark.html", title = "", assessment = assessment)

@app.route('/calculate_mark/assessment/<int:assessment_id>')
def calculate_mark_assessment(assessment_id):
    assessment = Assessment.query.filter_by(id=assessment_id).first()
    if assessment.is_calculated==True:
        return redirect(url_for("calculate_mark_results", assessment_id = assessment_id))
    return render_template("calculate_mark_assessment.html", assessment_id = assessment_id)

@app.route('/calculate_mark/criteria/<int:assessment_id>/<int:criteria_id>')
def calculate_mark_criteria_set(assessment_id, criteria_id):
    option_a = [(130, 110), (70, 100), (30, 80), (0, 0)]
    option_b = [(140, 110), (80, 100), (40, 80), (0, 0)]
    if criteria_id==1:
        criteria=option_a
    else:
        criteria=option_b
    for ind,per in criteria:
        newBW = BandWeighting(assessment=assessment_id, contribution_avg=ind, teamMark_percentage=per)
        db.session.add(newBW)
        db.session.commit()
    return redirect(url_for("calculate_mark_run",assessment_id = assessment_id))

@app.route('/calculate_mark/run/<int:assessment_id>')
def calculate_mark_run(assessment_id):
    teams = Team.query.filter_by(assessment_id=assessment_id).all()
    marking_tier = BandWeighting.query.filter_by(assessment=assessment_id).order_by(BandWeighting.contribution_avg.desc()).all()
    for team in teams:
        mark = {}
        for form in team.contribution_forms:
            student = form.student_evaluated
            if student not in mark: mark[student]=0
            for answer in form.contribution_answers:
                mark[student]+=answer.answer
        team_average = mean(mark.values())
        for i,j in mark.items():
            team_mark_index=int(round(100*j/team_average,0))
            for criteria in marking_tier:
                if team_mark_index>criteria.contribution_avg:
                    student_mark_percentage = criteria.teamMark_percentage
                    break
            newTMP = TeamMarkPercentage(assessment_id=assessment_id, student=i,team_mark_percentage=student_mark_percentage)
            db.session.add(newTMP)
            db.session.commit()
            print(newTMP)
        print(team.id, mark, mean(mark.values()))
    assessment = Assessment.query.filter_by(id=assessment_id).first()
    assessment.is_calculated = True
    db.session.commit()
    return redirect(url_for('calculate_mark_results', assessment_id = assessment_id))

@app.route('/calculate_mark/result/<int:assessment_id>')
def calculate_mark_results(assessment_id):
    result = TeamMarkPercentage.query.filter_by(assessment_id=assessment_id).all()
    assessment = Assessment.query.filter_by(id = assessment_id).first()
    return render_template( 'calculate_mark_results.html', result = result, assessment = assessment)

@app.route('/calculate_mark/csv/<int:assessment_id>')
def calculate_mark_result_csv(assessment_id):
    assessment = Assessment.query.filter_by(id = assessment_id).first()
    output = []
    for team in assessment.student_team_list:
        for user in team.team_members:
            current = str(user.team_id)+","+user.first_name+" "+user.last_name+","+str(user.team_mark_percentage[0].team_mark_percentage)
            output.append(current)
    return render_csv("Team ID, Student Name, Percentage", output, non_repr=0, filename="mark.csv")
            
#Contribution
@app.route("/contribution", methods=['GET','POST'])
def contribution():
    if len(Assessment.query.filter_by(id=1).first().student_team_list) == 0:
        flash("Teams have not been allocated!")
        return redirect(url_for('home'))

    form=EvaluationForm()
    #List all group members
    member = User.query.filter_by(team_id=current_user.team_id).all()
    group_menber = []
    for i in member:
        group_menber.append((i.id, i.first_name+" "+i.last_name ))
    form.student_evaluated.choices=group_menber
    #List all questions
    #questions = ContributionQuestion.query.filter_by(assessment_id=1)
    #group_menber1 = []
    #for i in member:
     #   group_menber.append((i.id))
    #form.question.choices=group_menber1
    if form.validate_on_submit():
        #if question >=2 , how to separate them??
        conQues = ContributionQuestion.query.filter_by(assessment_id=1)
        #db.session.add(conQues)
        #db.session.commit()

        if ContributionForm.query.filter_by(team_id = current_user.team_id, student_submitter = current_user.id, student_evaluated =form.student_evaluated.data).first():
            flash("Already Submitted for this person!")    
            return redirect(url_for('contribution'))
        conForm = ContributionForm(team_id = current_user.team_id, student_submitter = current_user.id, student_evaluated =form.student_evaluated.data)
        db.session.add(conForm)
        db.session.commit()


        for question in conQues:
            conAnswer = ContributionFormAnswers(form_id = conForm.id, question_id = question.id, answer = form.question.data )
            db.session.add(conAnswer)
            db.session.commit()
        flash("Your evaluation submitted successfully.")
        return redirect(url_for('contribution'))
    return render_template('peer_self_forms.html', title='Contribution', form=form)
    
 

# Customized Scripts

@app.route("/utility/batch_register")
def batch_register():
    assignment = Assessment(id=1,module_info="Test Module 1")
    db.session.add(assignment)
    db.session.commit()
    user=User(id=1,email="test"+"teacher"+"@test.in",password="Test1234",first_name="Test",last_name="Teacher",assessment_id=1,is_student=0)
    db.session.add(user)
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
    assessment = Assessment.query.filter_by(id=1).first()
    assessment.is_calculated = 0
    db.session.commit()
    flash("Reset completed.")
    return redirect(url_for('home'))


@app.route("/utility/reset_teams")
def reset_teams():
    for i in range(1001,1099,1):
        user= User.query.filter_by(id=i).first()
        user.team_id=None
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
    assessment = Assessment.query.filter_by(id=1).first()
    assessment.is_calculated = 0
    db.session.commit()
    flash("Teams have been reset.")
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
