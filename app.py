from flask import Flask, render_template, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserRegistration, UserLogin, FeedbackForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return redirect('/login')
 


@app.route('/users/<username>', methods=['GET'])
def show_user_details(username):
    if username == session['username']:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.all()
        return render_template("details.html", user=user, all_feedback=feedback)
    else:
        flash("Please login first!", "danger")
        return redirect('/login')
    


@app.route('/users/<username>/feedback/add', methods=['GET'])
def show_feedback_form(username):
    if username != session['username']:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = FeedbackForm()
    return render_template("feedback.html", form=form)

@app.route('/users/<username>/feedback/add', methods=['POST'])
def get_feedback(username):
    if username != session['username']:
        flash("Please login first!", "danger")
        return redirect('/login')
    form = FeedbackForm()
    title = form.title.data
    content = form.content.data
    new_feeback = Feedback(title=title, content=content, username=username)
    db.session.add(new_feeback)
    db.session.commit()
    flash('Feedback Created!', 'success')
    return redirect(f'/users/{username}')

  

@app.route('/register', methods=['GET'])
def display_register_user():
    form = UserRegistration()
    return render_template('register.html', form=form)


@app.route('/register', methods=['POST'])
def process_register_user():
    form = UserRegistration()
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    new_user = User.register(username, password, email, first_name, last_name)

    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        form.username.errors.append('Username taken.  Please pick another')
        return render_template('register.html', form=form)
    session['username'] = new_user.username
    flash('Welcome! Successfully Created Your Account!', "success")
    return redirect(f'/users/{username}')




@app.route('/login', methods=['GET'])
def display_login():
    form = UserLogin()
    return render_template('login.html', form=form)



@app.route('/login', methods=['POST'])
def login_user():
    form = UserLogin()
    username = form.username.data
    password = form.password.data

    user = User.authenticate(username, password)
    if user:
        flash(f"Welcome Back, {user.username}!", "primary")
        session['username'] = user.username
        return redirect(f'/users/{username}')
    else:
        flash("Invalid login!", "danger")
        return redirect('/login')





@app.route('/logout', methods=['GET'])
def logout_user():
    user = User.query.get_or_404(session['username'])
    session.pop('username')
    flash(f"Goodbye, {user.username}!", "info")
    return redirect('/login')


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Deletes a particular user"""
    if username == session['username']:
        user = User.query.get_or_404(username)
        if Feedback.query.filter_by(username = username) is not None:
            all_feedback = Feedback.query.filter_by(username = username).all()
            for feedback in all_feedback:
                db.session.delete(feedback)
        db.session.delete(user)
        db.session.commit()
        flash(F"{user.username} deleted!", "info")
    return redirect('/')





@app.route("/feedback/<feedback_id>/update", methods=["GET"])
def edit_feedback_form(feedback_id):
    """show edit feedback form"""
    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username
    if username == session['username']:
        form = FeedbackForm(obj=feedback)
        return render_template("edit_feedback.html", feedback=feedback, form=form)
    else:
        return redirect(f'/users/{username}')
    



@app.route('/feedback/<feedback_id>/update', methods=["POST"])
def edit_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)
    feedback.title = form.title.data
    feedback.content = form.content.data
    db.session.commit()
    return redirect(f"/users/{feedback.username}")



@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)
    if feedback.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")
