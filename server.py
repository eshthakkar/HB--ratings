"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                    session)
from flask_debugtoolbar import DebugToolbarExtension

from model import (connect_to_db, db, User, Rating, Movie)


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register',methods=["GET"])
def register_form():
    """ Show the Sign-in form"""

    return render_template("register_form.html")


@app.route('/register',methods=["POST"])
def register_process():
    """ User added to database"""

    user_name = request.form.get("email")
    password = request.form.get("password")
    check_user_in_db = User.query.filter(User.email == user_name).all()

    if check_user_in_db:
        flash("You've already signed up!")
        return redirect("/login")
    else:
        new_user = User(email=user_name, password=password) 
        db.session.add(new_user)
        db.session.commit()
        flash("You have been registered successfully!")
        return redirect("/")

@app.route('/login',methods=["GET"])
def login_form():
    """ Render login form."""

    return render_template("login_form.html")


@app.route('/login',methods=["POST"])
def login_process():
    """ Log the user in. """

    user_name = request.form.get("email")
    password = request.form.get("password")
    verify_user_info = User.query.filter(User.email == user_name, User.password == password).all()

    if verify_user_info:
        session['user_id'] = verify_user_info[0].user_id
        flash("Logged in as %s" % user_name)
        return redirect("/")
    else:
        flash("Invalid email/password")
        return redirect("/login")   

@app.route('/logout')
def logout():
    if 'user_id' in session:
        del session['user_id']
        flash("Logged Out!") 
        return redirect('/')   





if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    DEBUG_TB_INTERCEPT_REDIRECTS = False


    
    app.run(port=5000)
