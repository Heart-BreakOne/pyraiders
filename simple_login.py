import sys
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication
from helper_tools import perform_account_addition
from utils import constants
from utils.settings import open_file


#Receive user input before creating the qapp
name = input("""Type an unique account name and SR will open for you to log in.
*WARNING* This "browser" doesn't support openGL so it may crash *WARNING*
Enter the unique account name you want to add: """)
accounts = open_file(constants.py_accounts)
for account in accounts:
        if account["name"] == name or name == "" or name is None:
            #Stop execution here as the name is invalid.
            print("Please enter an unique account name.")
            sys.exit()
            
#Start qapp
app = QApplication([])

#Captures cookie of interest and save to storage.
def on_cookie_added(cookie):
    cookie_name = cookie.name().data().decode()
    cookie_value = cookie.value().data().decode()
    if cookie_name == "ACCESS_INFO":
        print("Adding account...")
        perform_account_addition(name, cookie_value)
        print("Added account for token: " + cookie_value)
        store.deleteAllCookies()
        view.close()

view = QWebEngineView()
page = QWebEnginePage()

#Access the cookie store via the page
store = page.profile().cookieStore()

#Clear existing cookies
store.deleteAllCookies()

# Connect a slot to the cookieAdded signal
store.cookieAdded.connect(on_cookie_added)

view.setPage(page)

# Load a URL
url = QUrl("https://www.streamraiders.com")
view.setUrl(url)

view.show()
app.exec_()