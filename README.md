# PyRaiders
## SR assistant written in Python.

### Requirements:
Python3.

### Non-mandatory requirements:
PyQt, QtWebEngine, selenium, chromedriver and a chromium based browser

Double click or execute ```python3 setup.py``` to install the Python dependencies.
Chromedriver and the browser must be installed manually. Ensure that they are compatible. Example: Chromedriver 120.0 == Chromium browser 120.0

## There are 3 ways to set up your account
Your account name is not necessarily the Twitch name, it's just a random unique name used to identify your account within PyRaiders.

To obtain the token, scapmpid and scsession open a browser, login to SR, right-click, Inspect elements, open dev tool -> Application -> Cookies -> SR website and get the values.

### Manual: 
Run ```python3 run.py``` once for the first time. It will create a py_accounts.json file with a template, use the template at the end of the page to add other new accounts.

### Guided:
Run ```python3 helper_tools add_account``` or ```python3 helper_tools a```
Follow the instructions, you will need the token, scapmpid and the scsession.

### Simplified (Requires PyQt and QtWebEngine)
Run ```python3 helpre_tools simple_login``` or ```python3 helpre_tools s```
Add your account name, a browser will load, login to your Twitch account.

You can add as many accounts as you want with any method you prefer, you don't have to use the same method everytime.

# Once you added at least one account double click or execute ```python3 run.py``` to start the assistant

## Determine which units should be used 
Run ```python3 helper_tools change_priority``` or ```python3 helper_tools c```
Type the name of the account, a list of units will load, copy and paste the id of the unit you want to edit and set a priority number.
0 -> Will be completely ignored.
1 -> Highest priority.
The higher the number, the lowest the priority. They all have a default of 1 meaning their priority is all the same.

## Quick access to your account (Requires selenium, chromedriver and a chromium browser)
After installing the chromedriver, go to the assistant folder /utils/ and edit the ```chrome_driver_path``` (8th line) at file ```constants.py``` with the path to your chromedriver.exe. Keep in mind that it's not the chromedriver folder, it's the chromedriver executable itself without the ".exe". There are path examples there to help you.

Run ```python3 helper_tools load_browser``` or ```python3 helper_tools l```
Add the name of the account you want to access then press ENTER.

## Use the following template when adding new accounts, you only need to add the unique account name, token, scapmpid and scsession, the rest is generated by the application.
## The assistant works perfectly fine with the default settings so you don't have to change if you don't want to.
Potions not yet implemented.
```json
    {
        "name": "",
        "token": "",
        "scapmpid": "",
        "scsession": "",
        "powered_on": True,
        "preserve_loyalty": 0,
        "switch_if_preserve_loyalty": False,
        "switch_on_idle": True,
        "minimum_idle_time": 15,
        "unlimited_campaign": False,
        "unlimited_clash": False,
        "unlimited_duels": False,
        "unlimited_dungeons": False,
        "any_captain": True,
        "only_masterlist": False,
        "masterlist": ["", "", ""],
        "ignore_blocklist": False,
        "blocklist": ["", "", ""],
        "temporary_ignore": [{"capNm": "", "time": ""}],
        "user_agent": "",
        "proxy": "",
        "proxy_user": "",
        "proxy_password": "",
        "user_potions": False,
        "has_pass": False,
        "userId": "",
        "otherUserId": "",
        "favorites_only": False,
        "favoriteCaptainIds": "",
        "slots": 3,
        "units": "",
    }
```