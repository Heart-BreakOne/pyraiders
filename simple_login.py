#import random
import sys
import time
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from helper_tools import perform_account_addition
from utils import constants
from utils.settings import open_file
ACCESS_INFO = None
scapmpid = None
scsession = None

# Receive user input before creating the qapp
print("This has not been implemented yet, at the moment the user agent can not be spoofed and thus the account origin can be easily detected.")
#sys.exit()
print("READ THIS WHILE YOU WAIT 10 SECONDS BEFORE PROCEEDING")
print("""The user agent of this login helper can not be spoofed, your login will be identified as:
Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_0) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.15.11 Chrome/87.0.4280.144 Safari/537.36
More specifically as QtWebEngine/5.15.11, this is enough to trace the unusual origin of the login, aiding on tracking bot accounts.
Therefore it is not advisable to use this login helper, if you know how to effectively spoof the QTWebEngine user agent please let me know.""")
time.sleep(10)
name = input("""Type an unique account name and SR will open for you to log in.
*WARNING* This "browser" doesn't support openGL so it may crash *WARNING*
Enter the unique account name you want to add: """
)
accounts = open_file(constants.py_accounts)
for account in accounts:
    if account["name"] == name or name == "" or name is None:
        # Stop execution here as the name is invalid.
        print("Please enter an unique account name.")
        sys.exit()

# Start qapp
app = QApplication([])

# Captures cookie of interest and save to storage.
def on_cookie_added(cookie):
    global ACCESS_INFO, scapmpid, scsession
    cookie_name = cookie.name().data().decode()
    cookie_value = cookie.value().data().decode()
    if cookie_name == "ACCESS_INFO":
        ACCESS_INFO = cookie_value
    elif cookie_name == "scapmpid":
           scapmpid = cookie_value
    elif cookie_name == "scsession":
        scsession = cookie_value
    if ACCESS_INFO != None and scapmpid != None and scsession != None:
        print("Adding account...")
        perform_account_addition(name, ACCESS_INFO, scapmpid, scsession)
        store.deleteAllCookies()
        view.close()


view = QWebEngineView()
page = QWebEnginePage()

# Access the cookie store via the page
store = page.profile().cookieStore()

# Clear existing cookies
store.deleteAllCookies()

#User agent spoofer that doesn't work
#view.page().profile().setHttpUserAgent(random.choice(constants.user_agents))

# Connect a slot to the cookieAdded signal
store.cookieAdded.connect(on_cookie_added)

user_agent = page.profile().httpUserAgent()
print("USER AGENT", user_agent)
view.setPage(page)

# Load a URL
url = QUrl("https://www.streamraiders.com")
view.setUrl(url)

view.show()
app.exec_()
