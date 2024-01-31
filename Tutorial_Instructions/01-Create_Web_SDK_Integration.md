# Cisco Live EMEA 2024

## DEVWKS-1698 - Using Cisco Duo APIs to add MFA to Web Applications

Now that the basic web application functionality has been validated, it is time to begin the process
of adding Cisco Duo Multi-factor Authentication (MFA) capabilities.

---

### Section 1 - Create Web SDK Integration in Duo Admin Panel

---

The first step in adding Cisco Duo Multi-factor Authentication (MFA) to an existing web
application is to define a new Web SDK integration in the Cisco Duo Admin Panel.

1. Navigate to [admin.duosecurity.com](http://admin.duosecurity.com) and login using the credentials defined during the
   trial account signup or an account with the *administrator* role in a Duo paid edition.
2. In the upper right of the Dashboard, select the `Add New... ` button and then select `Application`
   from the dropdown list.
3. Enter *SDK* in the **Protect an Application** filter input field. Select the `Protect` button to the
   right of the **Web SDK** item in the list.
4. Open the [duo.conf](../instance/duo.conf) file using the Visual Studio Code application (or a terminal based text
   editor, such as vim).
   - Copy the `Client ID`, `Client Secret`, and `API Hostname` to the corresponding lines in the `duo.conf` file.
   - Save the chanages to the `duo.conf` file.
5. Scroll down to the *Settings* section of the Web SDK application integration configuration page in the Duo Admin
   Panel and change the name to something more descriptive, such as Cisco Live DevNet Test. This name will display in
   the Duo MFA prompt shown to end users when they authenticate to the application.
   - Scroll to the bottom of the page and select the `Save` button.

The [next step](02-Add_Duo_to_Application.md) is to add the new code to the web application to add Cisco Duo MFA.

---

## Note

The `Client Secret` for the Web SDK application integration should be treated as a password. If at any point there
is a possibility that it has been compromised, it should be reset with a new value.