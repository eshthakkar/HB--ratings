"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request, flash,
                    session)
from flask_debugtoolbar import DebugToolbarExtension

from model import (connect_to_db, db, User, Rating, Movie)

from sqlalchemy.orm.exc import NoResultFound


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

@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by('title').all()
    return render_template("movie_list.html", movies=movies)


@app.route('/users/<int:user_id>')
def show_user_page(user_id):

    try:
        user = User.query.filter(User.user_id == user_id).one()
        return render_template("user.html",user=user)   
    except NoResultFound:
        flash("Nice try! User does not exist.")
        redirect("/users")


@app.route('/movies/<int:movie_id>')
def show_movie_page(movie_id):

    try:
        movie = Movie.query.filter(Movie.movie_id == movie_id).one()
        return render_template("movie.html",movie=movie)   
    except NoResultFound:
        flash("Nice try! Movie does not exist.")
        redirect("/movies")


@app.route('/register',methods=["GET"])
def register_form():
    """ Show the Sign-in form"""

    return render_template("register_form.html")


@app.route('/register',methods=["POST"])
def register_process():
    """ User added to database"""

    print request.form

    user_name = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    if not age:
        age = None
    zipcode = request.form.get("zipcode")
    if zipcode == "":
        zipcode = None
    check_user_in_db_query = User.query.filter(User.email == user_name)

    try:
        check_user_in_db_query.one()
        flash("You've already signed up!")
        return redirect("/login")

    except NoResultFound: 
        new_user = User(email=user_name, password=password, age=age, zipcode=zipcode) 
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
    verify_user_info = User.query.filter(User.email == user_name, User.password == password)

    try: 
        session['user_id'] = verify_user_info.one().user_id
        flash("Logged in as %s" % user_name)
        return redirect("/users/" + str(session['user_id']))
    except NoResultFound:
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

    
    app.run(port=5000)
