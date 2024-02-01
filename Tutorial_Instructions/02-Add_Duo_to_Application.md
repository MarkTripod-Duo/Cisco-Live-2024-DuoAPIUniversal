# Cisco Live EMEA 2024

## DEVWKS-1698 - Using Cisco Duo APIs to add MFA to Web Applications

With the necessary Duo Web SDK integration in place, it is time to update
the demonstration application to make use of the Cisco Duo service for MFA.

The `duo_univeral` [python library](https://github.com/duosecurity/duo_universal_python) will be used
to easily integrate the demonstration application with Duo APIs. The SDK provides automatic creation
of the necessary authentication headers as well as methods for easy access to all of the available API
endpoints.

---

### Section 1 - Add the Duo API functionality to the application

---

1. Stop the demonstration app if it is running.
2. Open the [app.py](../app.py) file in the Visual Studio Code application.
3. Add the following statements to the `import` statements at the top of the file (after line 18):

```python
import json
from duo_universal.client import Client, DuoException
```

4. Uncomment the SDK client code at the bottom of the app.py file by removing the lines that begin with `"""`

```python
    """ Uncomment this block for Duo configuration
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
    """
```

5. Replace the `login` function with the following code:

```python
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
                try:
                    duo_client.health_check()
                except DuoException:
                    if config.duo_failmode.upper() == "OPEN":
                        traceback.print_exc()
                        msg = ("Login 'Successful', but 2FA not performed."
                               + "Confirm Duo client/secret/host values are correct")
                        return render_template("home.html", message=msg)
                    else:
                        return render_template("login.html", message="2FA Unavailable.")
                state = duo_client.generate_state()
                session["state"] = state
                session["username"] = username
                prompt_uri = duo_client.create_auth_url(username, state)
                return redirect(prompt_uri)
        except NoResultFound:
            app_logger.warning("User %s does not exist.", username)
            error = "User %s is not registered." % username
            return render_template("login.html", error=error)
    # Display the login page if not a POST request
    return render_template("login.html", error=error)
```

6. Uncomment the `callback` route and function to handle redirects from Duo once MFA is complete.

```python
""" Uncomment this block for Duo
@app.route("/duo-callback")
def duo_callback():
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
"""
```

7. Save the changes and either wait for the application to automatically reload, or stop the
   program using the CTRL-C keystroke and then running the application again using the `python3 app.py` command.

8. Once the new code is in place and the application has been restarted, login with the user previously registered user.
   The Cisco Duo enrollment process should begin once the username and password are verified.
9. Save the changes to the `app.py` file.

The [next step](03-Test_Duo_Addition_to_Application.md) is to test the addition of Cisco Duo MFA to the application.

---

### Note

The full working application with Cisco Duo added and functional can be found in
the [app_with_duo.py](../app_with_duo.py) file for reference.