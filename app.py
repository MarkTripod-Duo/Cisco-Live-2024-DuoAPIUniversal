"""
Demo for basic web application with user authentication. To be used for
showing how to add Duo MFA authentication to an existing application.
"""
from __future__ import annotations, print_function

import argparse
import configparser
import os
from datetime import timedelta

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound

import duo_utils

# Uncomment the lines below for
# import json
# from duo_universal.client import Client, DuoException


app_logger = duo_utils.get_logger()

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = os.urandom(32)

bcrypt = Bcrypt(app)

db = SQLAlchemy()
db.init_app(app)
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


@login_manager.user_loader
def loader_user(user_id):
    """Retrieve user from DB"""
    try:
        return Users.query.session.execute(db.select(Users).where(Users.id == user_id))
    except NoResultFound:
        return None


@app.route('/register', methods=["GET", "POST"])
def register():
    """Register a new user"""
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
            user = db.session.execute(db.select(Users).filter_by(username=username)).scalar_one()
            if not bcrypt.check_password_hash(user.password, request.form.get("password")):
                error = "Invalid credentials."
                app_logger.error("Invalid credentials for %s", username)
            else:
                app_logger.info("Login successful for %s!", username)
                session["username"] = username
                login_user(user, remember=True, duration=timedelta(minutes=5.0))
                return redirect(url_for("home"))
        except NoResultFound:
            app_logger.warning("User %s does not exist.", username)
            error = "User %s is not registered." % username
            return render_template("login.html", error=error)
    # Display the login page if not a POST request
    return render_template("login.html", error=error)


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


def parse():
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

    return parser.parse_known_args()[0]


config = configparser.ConfigParser()
config.read("instance/duo.conf")

config_section = parse().config

""" Uncomment the following lines to enable the Cisco Duo SDK client
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
"""

duo_failmode = config[config_section]['failmode']

if __name__ == '__main__':
    app.run(host=config[config_section]['app_host'], port=int(config[config_section]['app_port']), debug=True)
