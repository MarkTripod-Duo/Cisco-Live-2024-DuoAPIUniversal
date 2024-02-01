"""
Demo for basic web application with user authentication. To be used for
showing how to add Duo MFA authentication to an existing application.
"""
from __future__ import annotations, print_function

import argparse
import configparser
import json
import os
import traceback

from duo_universal.client import Client, DuoException
from flask import Flask, flash, make_response, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound, NoSuchTableError

import duo_utils

DEBUG = False
cfg_file = "instance/duo.conf"
app_logger = duo_utils.get_logger()
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(32)
app.config['CACHE_TYPE'] = 'simple'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = os.urandom(32)

db = SQLAlchemy()


# The class definition below must be set before calling the db.init_app() and db.create_all() methods below.
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


@login_manager.user_loader
def loader_user(user_id):
    """Retrieve user from DB"""
    try:
        return Users.query.session.execute(db.select(Users).where(Users.id == user_id))
    except NoResultFound:
        return None


@app.route('/register', methods=["GET", "POST"])
def register():
    """Register a new user in the database"""
    # If the user made a POST request, create a new user
    if request.method == "POST":
        pswd = bcrypt.generate_password_hash(request.form.get('password')).decode()
        user = Users(username=request.form.get("username"),
                     password=pswd)
        # Add the user to the database
        db.session.add(user)
        db.session.commit()

        flash(f"User {user.username} successfully registered.")
        app_logger.info("User %s successfully registered.", user.username)
        # Send the user to the login page after successful registration
        return redirect(url_for("login"))
    # Respond with the registration page if not a POST request
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Display login screen"""
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        if username is None or username == "":
            app_logger.warning("Username is missing in login POST request.")
            error = "Username is missing in login POST request."
            return render_template("login.html", error=error)
        try:
            # Attempt to retrieve the entered username from the database
            user = db.session.execute(db.select(Users).filter_by(username=username)).scalar_one()
            if not bcrypt.check_password_hash(user.password, request.form.get("password")):
                error = "Invalid credentials."
                app_logger.error("Invalid credentials for %s", username)
            else:
                ##########################################################
                # This is where the Cisco Duo authentication flow begins #
                ##########################################################
                try:
                    # Check to make sure the Duo service is available
                    duo_client.health_check()
                except DuoException:
                    if config.duo_failmode.upper() == "OPEN":
                        traceback.print_exc()
                        msg = ("Login 'Successful', but 2FA not performed."
                               + "Confirm Duo client/secret/host values are correct")
                        return render_template("home.html", message=msg)
                    else:
                        # Duo failmode is set to 'secure' so login is prevented when Duo is unavailable
                        return render_template("login.html", message="2FA Unavailable.")
                # Generate a unique random state value for each authentication. This value should be store and compared
                # with the value that is sent to the callback() handler to verify the authentication has not been
                # tampered with. We do this my storing the value in the browser session.
                state = duo_client.generate_state()
                session["state"] = state
                session["username"] = username
                prompt_uri = duo_client.create_auth_url(username, state)
                duo_response_obj = make_response()
                # Redirect the browser to the Duo hosted authentication prompt
                return redirect(prompt_uri)
        except NoResultFound:
            # The entered username was not found in the database. This is likely caused by the user having not been
            # previously registered
            app_logger.warning("User %s does not exist.", username)
            error = "User %s is not registered." % username
            return render_template("register.html", error=error)
        except NoSuchTableError:
            # The 'users' table was not found in the database. This is likely due to a failure to initialize the
            # database or the database file missing.
            app_logger.error(f"The 'users' table is missing from the database.")
            error = "The 'users' table is missing from the database. Verify that the database is correct."
            return render_template("home.html")
    # Display the login page if not a POST request
    return render_template("login.html", error=error)


@app.route("/duo-callback")
def duo_callback():
    """Get state to verify consistency and originality"""
    state = request.args.get('state')

    # Get authorization token to trade for 2FA
    code = request.args.get('duo_code')

    if 'state' in session and 'username' in session:
        saved_state = session['state']
        username = session['username']
    else:
        # For flask, if url used to get to login.html is not localhost,
        # (ex: 127.0.0.1) then the sessions will be different
        # and the localhost session does not have the state
        return render_template("login.html",
                               message="No saved state. Please login again")

    # Ensure nonce matches from initial request
    if state != saved_state:
        return render_template("login.html",
                               message="Duo state does not match saved state")

    try:
        decoded_token = duo_client.exchange_authorization_code_for_2fa_result(code, username)
    except DuoException as duo_exception:
        app_logger.exception(f"Unable to exchange authorization code for token: {duo_exception}")
        return render_template("login.html", error=duo_exception)

    # Exchange happened successfully so render success page
    # return render_template("success.html",
    #                        message=json.dumps(decoded_token, indent=2, sort_keys=True))
    user = db.session.execute(db.select(Users).filter_by(username=username)).scalar_one()
    if login_user(user):
        app_logger.info("User %s logged in and added to session successfully.", username)
        session["username"] = username
        return render_template("home.html",
                               message=json.dumps(decoded_token, indent=2, sort_keys=True), username=username)
    else:
        app_logger.warning("Unable to add user %s to session successfully.", username)
        return render_template("home.html", error="Unable to add user to session information.")


@app.route("/logout")
def logout():
    """Log user out and redirect to home page"""
    if 'username' in session:
        app_logger.info("User %s logged out.", session['username'])
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


def process_args():
    """Process command line arguments"""
    parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
            "-c",
            "--config",
            help="The config section from duo.conf to use",
            default="duo",
            metavar=''
    )

    parser.add_argument(
            "-f",
            "--file",
            help=f"Path to configuration file. [Default: ./instance/duo.conf]",
            metavar="config_file"
    )

    parser.add_argument(
            "--debug",
            "-d",
            help="Enable debug mode.",
            action="store_true",
            default=False,

    )
    return parser.parse_known_args()[0]


if __name__ == '__main__':
    args = process_args()
    cfg_file = args.file if args.file is not None else "instance/duo.conf"
    config_section = args.config
    config = configparser.ConfigParser()
    config.read(cfg_file)

    try:
        duo_client = Client(
                client_id=config[config_section]['client_id'],
                client_secret=config[config_section]['client_secret'],
                host=config[config_section]['api_hostname'],
                redirect_uri=config[config_section]['redirect_uri'],
                duo_certs=config[config_section].get('duo_certs'),
        )
    except DuoException as e:
        print("*** Duo config error. Verify the values in duo.conf are correct ***")
        raise e

    duo_failmode = config[config_section]['failmode']

    app.run(host=config[config_section]['app_host'], port=int(config[config_section]['app_port']), debug=True)
