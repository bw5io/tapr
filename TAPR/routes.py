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
