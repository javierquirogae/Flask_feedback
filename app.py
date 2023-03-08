from flask import Flask, render_template, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserRegistration, UserLogin, FeedbackForm
from sqlalchemy.exc import IntegrityError

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
    return redirect('/register')
 


@app.route('/users/<username>', methods=['GET'])
def show_user_details(username):
    if username == session['username']:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.all()
        return render_template("details.html", user=user, all_feedback=feedback)
    else:
        flash("Please login first!", "danger")
        return redirect('/login')
    

# id - a unique primary key that is an auto incrementing integer
# title - a not-nullable column that is at most 100 characters
# content - a not-nullable column that is text
# username - a foreign key that references the username column in the users table

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

  


# @app.route('/tweets/<int:id>', methods=["POST"])
# def delete_tweet(id):
#     """Delete tweet"""
#     if 'user_id' not in session:
#         flash("Please login first!", "danger")
#         return redirect('/login')
#     tweet = Tweet.query.get_or_404(id)
#     if tweet.user_id == session['user_id']:
#         db.session.delete(tweet)
#         db.session.commit()
#         flash("Twich deleted!", "info")
#         return redirect('/tweets')
#     flash("You don't have permission to do that!", "danger")
#     return redirect('/tweets')


@app.route('/register', methods=['GET'])
def display_register_user():
    form = UserRegistration()
    return render_template('register.html', form=form)


@app.route('/register', methods=['POST'])
def process_register_user():
    form = UserRegistration()
    # username - a unique primary key that is no longer than 20 characters.
    # password - a not-nullable column that is text
    # email - a not-nullable column that is unique and no longer than 50 characters.
    # first_name - a not-nullable column that is no longer than 30 characters.
    # last_name - a not-nullable column that is no longer than 30 characters.
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
        return redirect('login.html')





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


# @app.route('/api/tweets/<int:id>', methods=["DELETE"])
# def delete_tweet_via_api(id):
#     """Deletes a particular tweet"""
#     tweet = Tweet.query.get_or_404(id)
#     print('-'*100)
#     print(id)
#     db.session.delete(tweet)
#     db.session.commit()
#     return jsonify(message="deleted")
