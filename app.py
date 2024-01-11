"""
Demo for basic web application with user authentication. To be used for
showing how to add Duo MFA authentication to an existing application.
"""

from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user


HOME_TITLE = 'Example Web Application'


app = Flask(__name__)
# Tells flask-sqlalchemy what database to connect to
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
# Enter a secret key
app.config["SECRET_KEY"] = "304394495a2d7fb18325537ce16c5ff64e9492db53b85806fd48e22a43a09f35adf48867"
# Initialize flask-sqlalchemy extension
db = SQLAlchemy()

# LoginManager is needed for our application
# to be able to log in and out users
login_manager = LoginManager()
login_manager.init_app(app)


# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True,
                         nullable=False)
    password = db.Column(db.String(250),
                         nullable=False)


db.init_app(app)
with app.app_context():
    db.create_all()


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    """Retrieve user from DB"""
    return Users.query.get(user_id)


@app.route('/register', methods=["GET", "POST"])
def register():
    """Register a new user"""
    # If the user made a POST request, create a new user
    if request.method == "POST":
        user = Users(username=request.form.get("username"),
                     password=request.form.get("password"))
        # Add the user to the database
        db.session.add(user)
        # Commit the changes made
        db.session.commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("login"))
    # Renders sign_up template if user made a GET request
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Display login screen"""
    # If a post request was made, find the user by
    # filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(
                username=request.form.get("username")).first()
        # Check if the password entered is the
        # same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            session["username"] = user.username
            login_user(user)
            return redirect(url_for("home"))
    # Redirect the user back to the home
    # (we'll create the home route in a moment)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out and redirect to home page"""
    session.pop('username', None)
    logout_user()
    return redirect(url_for("home"))


@app.route("/")
def home():
    """Display home page"""
    # Render home.html on "/" route
    if "username" in session:
        username = session.get("username")
    else:
        username = None
    return render_template("home.html", title=HOME_TITLE, username=username)


if __name__ == '__main__':
    app.run()
