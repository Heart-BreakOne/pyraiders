from utils.settings import write_file
from utils import constants


def create_account():
    default_entry = [
        {
            "name": "",
            "token": "",
            "powered_on": True,
            "preserve_loyalty": 0,
            "switch_if_no_loyalty": False,
            "switch_on_idle": True,
            "minimum_idle_time": 15,
            "unlimited_campaign": True,
            "unlimited_clash": True,
            "unlimited_dungeons": True,
            "unlimited_clash": True,
            "any_captain": True,
            "only_masterlist": False,
            "masterlist": ["", "", ""],
            "ignore_blacklist": False,
            "blacklist": ["", "", ""],
            "temporary_ignore": {"cptName": 0},
            "user_agent": "",
            "proxy": "",
            "userId": "",
            "favoriteCaptainIds": "",
            "units": ""
        },
        {
            "name": "",
            "token": "",
            "powered_on": True,
            "preserve_loyalty": 0,
            "switch_if_no_loyalty": False,
            "switch_on_idle": True,
            "minimum_idle_time": 15,
            "unlimited_campaign": True,
            "unlimited_clash": True,
            "unlimited_dungeons": True,
            "unlimited_clash": True,
            "any_captain": True,
            "only_masterlist": False,
            "masterlist": ["", "", ""],
            "ignore_blacklist": False,
            "blacklist": ["", "", ""],
            "temporary_ignore": {"cptName": 0},
            "user_agent": "",
            "proxy": "",
            "userId": "",
            "favoriteCaptainIds": "",
            "units": ""
        }
    ]
    
    write_file(constants.py_accounts, default_entry)

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
