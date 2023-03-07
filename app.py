from flask import Flask, render_template, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    if "user_id" in session:
        return redirect('/tweets')
    return render_template('index.html')


@app.route('/tweets', methods=['GET'])
def show_tweets():
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = TweetForm()
    all_tweets = Tweet.query.all()
    return render_template("tweets.html", form=form, tweets=all_tweets)



@app.route('/tweets', methods=['POST'])
def tweet():
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = TweetForm()
    text = form.text.data
    new_tweet = Tweet(text=text, user_id=session['user_id'])
    db.session.add(new_tweet)
    db.session.commit()
    flash('Twich Created!', 'success')
    return redirect('/tweets')

  




@app.route('/tweets/<int:id>', methods=["POST"])
def delete_tweet(id):
    """Delete tweet"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash("Twich deleted!", "info")
        return redirect('/tweets')
    flash("You don't have permission to do that!", "danger")
    return redirect('/tweets')


@app.route('/register', methods=['GET'])
def display_register_user():
    form = UserForm()
    return render_template('register.html', form=form)


@app.route('/register', methods=['POST'])
def process_register_user():
    form = UserForm()
    username = form.username.data
    password = form.password.data
    new_user = User.register(username, password)

    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError:
        form.username.errors.append('Username taken.  Please pick another')
        return render_template('register.html', form=form)
    session['user_id'] = new_user.id
    flash('Welcome! Successfully Created Your Account!', "success")
    return redirect('/tweets')




@app.route('/login', methods=['GET'])
def display_login():
    form = UserForm()
    return render_template('login.html', form=form)



@app.route('/login', methods=['POST'])
def login_user():
    form = UserForm()
    username = form.username.data
    password = form.password.data

    user = User.authenticate(username, password)
    if user:
        flash(f"Welcome Back, {user.username}!", "primary")
        session['user_id'] = user.id
        return redirect('/tweets')
    else:
        flash("Invalid login!", "danger")
        return redirect('/tweets')





@app.route('/logout')
def logout_user():
    user = User.query.get_or_404(session['user_id'])
    session.pop('user_id')
    flash(f"Goodbye, {user.username}!", "info")
    return redirect('/')


@app.route('/api/users/<int:id>', methods=["DELETE"])
def delete_user(id):
    """Deletes a particular user"""
    user = User.query.get_or_404(id)
    if Tweet.query.filter_by(user_id = id) is not None:
        tweets = Tweet.query.filter_by(user_id = id).all()
        for tweet in tweets:
            db.session.delete(tweet)
    db.session.delete(user)
    db.session.commit()
    return jsonify(message="deleted")


@app.route('/api/tweets/<int:id>', methods=["DELETE"])
def delete_tweet_via_api(id):
    """Deletes a particular tweet"""
    tweet = Tweet.query.get_or_404(id)
    print('-'*100)
    print(id)
    db.session.delete(tweet)
    db.session.commit()
    return jsonify(message="deleted")
