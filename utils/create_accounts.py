from utils.settings import write_file
from utils import constants


def create_account():
    
    write_file(constants.py_accounts, constants.default_entry)

    print("*Accounts file created successfully.")
    print("*To add multiple accounts simply copy and paste the default account.")
    print("*Add unique names and unique tokens.")
    print(
        "*The name can be anything you want, they don't have to be the Twitch account. Tokens must match your account."
    )
    print("*Customize the other settings as you need.")
    print("*Accounts with duplicate names and tokens will be wiped from the file.")
    print("*If you have any issues with the user agent or the proxy, replace them.")
    print(
        "*Duplicate user agents and proxies will be automatically replaced, you can manually edit if you have issues with faulty ones, but make sure they are not duplicates."
    )
    print("*Once the file is set up, run main.py again.")
