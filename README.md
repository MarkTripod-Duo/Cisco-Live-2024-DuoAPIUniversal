# Cisco Live EMEA 2024
# DEVWKS-1698 - Using Cisco Duo APIs to add MFA to Web Applications

Thank you for spending the next 45 minutes with me. Once we are complete, 
you will have successfully completed an integration of Cisco Duo  MFA 
functionality into a web application.

## Overview

Today we will take a simple web-based application that has user registration
and login functionality and add Cisco Duo Multi-factor Authentication (MFA) using
the Cisco Duo Web SDK integration.

The [Cisco Duo Web SDK integration](https://duo.com/docs/duoweb) provides a seamless addition of two factor
authentication
using browser redirects.

### Pre-requisites

Before we can begin, there are a few items that need to be in place and ready.

They are:

- Mobile phone or tablet (iOS or Android)
- Cisco Duo account
  - https://signup.duo.com

----

### Section 1 - Start the demonstration application

----
Begin by starting the the demonstration application.

1. In the command terminal navigate to the root project `DuoAPI` directory
2. Make sure all of the required python modules are installed by running `pip3 install -r requirements.txt`
3. Run the command `python3 app.py run` in the command terminal to start the demonstration application
4. Open a web browser and follow the link provided in the output of the demonstration application initialization
5. Register a user with the application by selecting the `REGISTER` button in the blue menubar.
6. Now that the application is running and a user has been registered,
   the [next step](Tutorial_Instructions/01-Create_Web_SDK_Integration.md) is to add Cisco Duo MFA.

----

### Note

There are many choices available via the Cisco Duo Administration Panel to control
how integration with applications behave. This exercise is meant solely as an
illustration of how easy it is to get started.