"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """ Provide helpful representation of user when printed"""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

    def similarity(self, other):
        """Return pearson rating for user1 compared to user2."""

        u_ratings = {}
        paired_ratings = []

        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in other.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.score, r.score) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0  

    def predict_rating(self, movie):
        """Predict a user's rating of a movie."""

        other_ratings = movie.ratings
        other_users = [ r.users_info for r in other_ratings ]

        similarities = [
            (self.similarity(other_user), other_user)
            for other_user in other_users
        ]

        similarities.sort(reverse=True)
        sim, best_match_user = similarities[0]

        matched_rating = None
        for rating in other_ratings:
            if rating.user_id == best_match_user.user_id:
               return rating.score * sim          



class Rating(db.Model):
    """Rating of users for movies"""

    # Ask about foreign keys

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True,)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    users_info = db.relationship("User",backref=db.backref("ratings",
                                                           order_by=rating_id))
    movie_info = db.relationship("Movie",backref=db.backref("ratings",
                                                           order_by=rating_id))

    def __repr__(self):
        """ Provide helpful representation of rating when printed"""

        return "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>" % (self.rating_id, self.movie_id, self.user_id, self.score)

class Movie(db.Model):
    """Movies to rate"""

    # Ask about foreign keys

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True,)
    title = db.Column(db.String(150), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imdb_url = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        """ Provide helpful representation of movie when printed"""

        return "<Movie movie_id=%s title=%s released_at=%s>" % (self.movie_id, self.title, self.released_at)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."