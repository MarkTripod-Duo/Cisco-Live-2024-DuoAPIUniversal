"""
Demo for basic web application with user authentication. To be used for
showing how to add Duo MFA authentication to an existing application.
"""

from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user

import duo_client

IKEY = 'DI8H6LDLJZ58SV9CMTNT'
SKEY = 'j0yDaRHkw5FtjetzU39gkd6iIguMn9brwluhbTUu'
API_HOST = 'api-731c6826.duosecurity.com'

auth_client = duo_client.Auth(
        ikey=IKEY,
        skey=SKEY,
        host=API_HOST
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "304394495a2d7fb18325537ce16c5ff64e9492db53b85806fd48e22a43a09f35adf48867"

db = SQLAlchemy()
db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


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
    error = None
    if request.method == "POST":
        user = Users.query.filter_by(
                username=request.form.get("username")).first()
        # Check if the password entered is the same as the user's password
        if user.password != request.form.get("password"):
            error = "Invalid credentials."
        else:
            if not ping_duo():
                error = f"Duo service is unreachable. Please try again."
                return render_template("login.html", error=error)
            if not check_duo():
                error = f"Provided Duo API credentials are invalid. Please verify the IKEY, SKEY and API_HOST values."
                return render_template("login.html", error=error)
            session["username"] = user.username
            result = duo_auth(user.username)
            if result[0] in ["Success", "Bypass"]:
                login_user(user)
                return redirect(url_for("home"))
            elif result[0] == "Enroll":
                return redirect(result[1])
            elif result[0] == "Deny":
                return redirect(url_for("logout"))
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    """Log user out and redirect to home page"""
    session.pop('username', None)
    logout_user()
    return redirect(url_for("home"))


@app.route("/")
def home():
    """Display home page"""
    if "username" in session:
        username = session.get("username")
    else:
        username = None
    return render_template("home.html", username=username)


def ping_duo() -> bool:
    """Verify that the Duo service is available"""
    duo_ping = auth_client.ping()
    return True if 'time' in duo_ping else False


def check_duo() -> bool:
    """Verify that IKEY and SKEY information provided are valid"""
    duo_check = auth_client.check()
    return True if 'time' in duo_check else False


def duo_auth(username: str = None) -> tuple:
    """Perform Duo MFA"""

    # Execute pre-authentication for given user
    print(f"\nExecuting pre-authentication for {username}...")
    pre_auth = auth_client.preauth(username=username)

    if pre_auth['result'] == "auth":
        try:
            # User exists and has an MFA device enrolled
            print(f"Executing authentication action for {username}...")
            # "auto" is selected for the factor in this example, however the pre_auth['devices'] dictionary
            # element contains a list of factors available for the provided user, if an alternate method is desired
            auth = auth_client.auth(factor="auto", username=username, device="auto")
            print(f"\n{auth['status_msg']}")
            return "Success", None
        except Exception as e_str:
            print(e_str)
    elif pre_auth['result'] == "allow":
        # User is in bypass mode
        print(pre_auth['status_msg'])
        return "Bypass", None
    elif pre_auth['result'] == "enroll":
        # User is unknown and not enrolled in Duo with a 'New User' policy setting of 'Require Enrollment'
        # Setting a 'New User' policy to 'Require Enrollment' should only be done for Group level policies where
        # the intent is to capture "partially enrolled" users. "Partially enrolled" users are those that Duo has a
        # defined username but does not have an MFA device enrolled.
        print("Please enroll in Duo using the following URL.")
        print(pre_auth['enroll_portal_url'])
        return "Enroll", pre_auth['enroll_portal_url']
    elif pre_auth['result'] == "deny":
        # User is denied by policy setting
        print(pre_auth['status_msg'])
        return "Deny", None
    else:
        print("Error: an unexpected error occurred")
        print(pre_auth)
        return "Error", None


if __name__ == '__main__':
    app.run()
