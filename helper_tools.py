# This is a command line helper

import sys, time
from utils.game_requests import set_user_data
from utils.settings import setup_accounts, write_file, open_file
from utils import constants
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


usage = "Usage: python3 helper_tools.py <command>\nCommands:\nadd_account or a\nchange_priority or c\nload_browser or l"


def perform_account_addition(name, token):
    print("This may take a few seconds...")
    if name != None and token != None:
        new_account = constants.default_entry
        entry = new_account[0]
        entry["name"] = name
        entry["token"] = token

        existing_data = open_file(constants.py_accounts)
        if existing_data != None:
            existing_data.append(entry)
        else:
            existing_data = new_account

        existing_data = setup_accounts(existing_data)
        existing_data = set_user_data(existing_data)

        write_file(constants.py_accounts, existing_data)
        print("Account added.")


def add_account():
    name = input("Enter an unique account name: ")
    token = input("Enter account token: ")
    perform_account_addition(name, token)


def change_priority():
    # todo load list of units, print unit and unit id to the user.
    user_account = input(
        "Enter the account name or the account Id you want to change the unit priority for: "
    )
    accounts = open_file(constants.py_accounts)

    for account in accounts:
        if (
            account["name"] == user_account
            or account["userId"] == user_account
            or account["otherUserId"] == user_account
        ):
            for unit in account["units"]:
                print(
                    f'UNIT ID: {unit["unitId"]}   Current priority: {unit["priority"]}.    Unit: {unit["unitType"]}. Level: {unit["level"]}. Specialization: {unit["specializationUid"]}'
                )
            break

    unit_id = input("Enter the unit id you want to change the priority for: ")
    priority = input("Enter the new unit priority: ")

    if unit_id == None or priority == None:
        print("Please type a valid id or priority")
        return
    if priority is not None:
        try:
            int_priority = int(priority)
        except ValueError:
            print(f"Please insert a valid priority number")
            return
    break_all_loops = False
    for account in accounts:
        if break_all_loops:
            break
        if (
            account["name"] == user_account
            or account["userId"] == user_account
            or account["otherUserId"] == user_account
        ):
            for unit in account["units"]:
                if unit["unitId"] == unit_id:
                    unit["priority"] = int_priority
                    print(f"Priority for unit {unit_id} updated.")
                    break_all_loops = True
                    break

    write_file(constants.py_accounts, accounts)


def load_browser():
    name = input("Enter the account name you want to open a browser for: ")
    accounts = open_file(constants.py_accounts)
    ACCESS_INFO = None
    found = False
    for account in accounts:
        if account["name"] == name:
            ACCESS_INFO = account["token"]
            found = True
            break
    if not found:
        print("Type an account you would like to access")
        
    if ACCESS_INFO is not None:
        try:
            chrome_options = Options()
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://www.streamraiders.com")
            driver.add_cookie(
                {
                    "name": "ACCESS_INFO",
                    "value": ACCESS_INFO,
                    "domain": ".www.streamraiders.com",
                    "path": "/",
                }
            )
            driver.refresh()
            print("Opening SR tab for " + name + "...\n Press CTRL+C to close browser.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                driver.quit()
        except:
            pass


def main():
    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    command = sys.argv[1]

    if command == "add_account" or command == "a":
        add_account()
    elif command == "change_priority" or command == "c":
        change_priority()
    elif command == "load_browser" or command == "l":
        load_browser()
    else:
        print(f"Unknown command: {command} \n{usage}")


if __name__ == "__main__":
    main()
