# Cisco Live EMEA 2024

## DEVWKS-1698 - Using Cisco Duo APIs to add MFA to Web Applications

Thank you for spending the next 45 minutes with me. When this session is complete,
we will have successfully completed an integration of Cisco Duo MFA
functionality into a web application.

## Overview

Today we will take a simple web-based application built with Flask that has user registration
and login functionality and add Cisco Duo Multi-factor Authentication (MFA) using
the Cisco Duo Web SDK integration.

The [Cisco Duo Web SDK integration](https://duo.com/docs/duoweb) provides a seamless addition of two factor
authentication using browser redirects.

### Pre-requisites

Before we can begin, there are a few items that need to be in place and ready.

They are:

- Firm understanding of the Python programming language
- Basic understanding of the HTTP protocol (communication methods, URI redirection)
- Basic understanding of the Python Flask package
- Mobile phone or tablet (iOS or Android)
- Cisco Duo account (either existing paid account or trial account)
    - [signup.duo.com](https://signup.duo.com) (to create a new trial Cisco Duo account)
        - Requires a valid email address used during the initial verification process

----

### Section 1 - Prepare the development environment

----

1. Clone this repository or download the ZIP file and unpack the contents
2. Open a terminal window and navigate to the root folder of the project (`./DuoAPIUniversal`).
3. Create a virtual environment using the command `python3 -m venv .`
4. Activate the virtual environment:
    - The syntax of the activation command is platform
      specific ([see here](https://docs.python.org/3/library/venv.html#how-venvs-work) for details)
        - For linux platforms using bash/zsh: `source ./bin/activate`
        - For Windows platforms:
            - Powershell: `.\Scripts\Activate.ps1`
            - CMD.exe: `.\Scripts\activate.bat`
5. Install the required Python packages: `python3 -m pip install -r requirements.txt`

----

### Section 2 - Start the demonstration application

----
Begin by starting the demonstration application.

1. In the command terminal navigate to the root project `./DuoAPIUniversal` directory
2. Run the command `python3 app.py run` in the command terminal to start the demonstration application
3. Open a web browser and follow the link provided in the output of the demonstration application initialization (the
   default is http://localhost:8008)
4. Register a user with the application by selecting the `REGISTER` button in the blue menubar.
5. Now that the application is running and a user has been registered,
   the [next step](Tutorial_Instructions/01-Create_Web_SDK_Integration.md) is to add Cisco Duo MFA.

----

### Note

There are many choices available via the Cisco Duo Administration Panel to control
how integration with applications behave. This exercise is meant solely as an
illustration of how easy it is to get started. In a typical production deployment, specific Duo Policy settings are
put in place to control various aspects of the end user experience as well as implement any business security
requirements.