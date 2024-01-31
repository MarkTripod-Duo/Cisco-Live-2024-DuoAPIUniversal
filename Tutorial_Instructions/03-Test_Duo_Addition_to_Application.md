# Cisco Live EMEA 2024

## DEVWKS-1698 - Using Cisco Duo APIs to add MFA to Web Applications

With the addition of Cisco Duo MFA to the application in place, it is time to test the demonstration application.

---

### Section 1 - Run the application

---

1. Open a terminal window and navigate to the root folder of the project (`./DuoAPIUniversal`).
2. Run the command `python3 app.py run` in the command terminal to start the demonstration application.
3. Open a web browser and follow the link provided in the output of the demonstration application initialization (the
   default is http://localhost:8008).
4. Select the `LOGIN` button from the menubar.
5. Enter the username and password that was registered in the beginning of this tutorial.

Once the primary username and password have been validated against the local database, the web browser should be
redirected to a Cisco Duo hosted web page. This page will prompt the user
to [enroll](https://guide.duo.com/universal-enrollment) in Duo if they have not
been enrolled previously.

Walk through the prompts to complete enrollment in Duo using
the [Duo mobile application](https://duo.com/product/multi-factor-authentication-mfa/duo-mobile-app).

Once enrollment in Duo is complete, the [Duo MFA process](https://guide.duo.com/universal-prompt) will begin.

Once the Cisco Duo MFA process is complete, the end user is returned to the demonstration application.

---

### Complete

---

This completes the tutorial for adding Cisco Duo MFA to a web application using the `duo_universal_python` web SDK.