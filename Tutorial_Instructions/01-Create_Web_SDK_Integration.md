# Cisco Live EMEA 2024

# DEVWKS-1698 - Using Cisco Duo APIs to add MFA to Web Applications

---

## 01 - Create Web SDK Integration in Duo Admin Panel

The first step in adding Cisco Duo Multi-factor Authentication (MFA) to an existing web
application, a new Web SDK integration must be created in the Cisco Duo Admin Panel.
Navigate to [admin.duosecurity.com](http://admin.duosecurity.com) and login using the credentials defined during the
trial account signup.

In the upper right of the Dashboard, select the `Add New... ` button and then select `Application`
from the dropdown list.

Enter *SDK* in the **Protect an Application** filter input field. Select the `Protect` button to the
right of the **Web SDK** item in the list.

Open the [duo.conf](../instance/duo.conf) file using the Visual Code application. Copy the `Client ID`, `Client Secret`,
and `API Hostname` to the corresponding lines in the `duo.conf` file.

The [next step](02-Add_Duo_to_Application.md) is to add the new code to the web application to add Cisco Duo MFA.