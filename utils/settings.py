import json
import random
import os
import requests
from utils import constants


# Get current game version and dataVersion. Validate user token, if not correct, return false
def get_user_data():
    gameDataResponse = requests.get(constants.gameDataURL)
    # Check if the request was successful (status code 200)
    if gameDataResponse.status_code == 200:
        # Print the response content
        response_json = gameDataResponse.json()

        # Extract version from the JSON response
        version = response_json["info"]["version"]
        data_version = response_json["info"]["dataVersion"]
        validateURL = (
            "https://www.streamraiders.com/api/game/?cn=getUser&gameDataVersion="
            + data_version
            + "&command=getUser&skipDataCheck=true&isLogin=true&clientVersion="
            + version
            + "&clientPlatform=WebGL"
        )

        settings_data = open_file(constants.py_captain)
        access_info = settings_data.get("access_info", {})
        user_agent = settings_data.get("user_agent", {})
        headers = {"Cookie": "ACCESS_INFO=" + access_info, "User-Agent": user_agent}

        response = requests.get(validateURL, headers=headers)
        if response.status_code == 200:
            currentResponse = response.json()
            isCaptain = currentResponse["data"]["isCaptain"]
            if isCaptain != "1":
                return False
            else:
                userId = currentResponse["data"]["userId"]
                captainUserName = currentResponse["data"]["twitchUserName"]
                data_to_save = {
                    "userId": userId,
                    "captainUserName": captainUserName,
                    "version": version,
                    "data_version": data_version,
                }

                existing_data = {}

                existing_data = open_file(constants.py_captain)
                existing_data.update(data_to_save)
                write_file(constants.py_captain, existing_data)
                return True
        else:
            return False
    else:
        # Print an error message if the request was not successful
        return False


def check_settings(file_to_check):
    if os.path.exists(file_to_check):
        return True
    else:
        return False

def save_settings(ACCESS_INFO):
    random_user_agent = random.choice(constants.user_agents)

    # Save the data to a JSON file
    data_to_save = {"access_info": ACCESS_INFO, "user_agent": random_user_agent}
    write_file(constants.py_captain, data_to_save)


def delete_settings():
    os.remove(constants.py_captain)

def open_file(file_name):
    try:
        with open(file_name, "r") as json_file:
            settings_data = json.load(json_file)
            return settings_data
    except FileNotFoundError:
        print(f"*Accounts file does not exist. Creating one...")


def write_file(file_name, data_to_save):
    with open(file_name, "w") as json_file:
        json.dump(data_to_save, json_file, indent=2)


def setup_accounts(data):
    #Generate unique user agent
    def generate_unique_user_agent(existing_user_agents):
        base_user_agent = random.choice(constants.user_agents)
        new_user_agent = f"{base_user_agent}_{random.randint(1, 1000)}"
        while new_user_agent in existing_user_agents:
            new_user_agent = f"{base_user_agent}_{random.randint(1, 1000)}"
        existing_user_agents.add(new_user_agent)
        return new_user_agent

    #Generate unique proxy
    def generate_unique_proxy(existing_proxies):
        base_proxy = random.choice(constants.proxies)
        new_proxy = f"{base_proxy}_{random.randint(1, 1000)}"
        while new_proxy in existing_proxies:
            new_proxy = f"{base_proxy}_{random.randint(1, 1000)}"
        existing_proxies.add(new_proxy)
        return new_proxy

    #Set of existing values
    existing_user_agents = set()
    existing_proxies = set()
    existing_names = set()
    existing_tokens = set()

    unique_accounts = []
    
    #Clean up the data.
    for account_data in data:
        # Remove entries with empty name or token strings
        if account_data["name"] != "" and account_data["token"] != "":
            # Check for duplicate names or tokens
            if (
                account_data["name"] in existing_names
                or account_data["token"] in existing_tokens
            ):
                continue

            # Replace none proxies
            if account_data["proxy"].lower() in ["none", ""]:
                account_data["proxy"] = ""

            # Add user agent if empty or duplicate
            if account_data["user_agent"] == "" or account_data["user_agent"] in existing_user_agents:
                account_data["user_agent"] = generate_unique_user_agent(existing_user_agents)

            # Add proxy if empty, "none", or duplicate
            if account_data["proxy"].lower() in ["none", ""] or account_data["proxy"] in existing_proxies:
                account_data["proxy"] = generate_unique_proxy(existing_proxies)
                
            existing_names.add(account_data["name"])
            existing_tokens.add(account_data["token"])
            existing_user_agents.add(account_data["user_agent"])
            existing_proxies.add(account_data["proxy"])

            unique_accounts.append(account_data)

    return unique_accounts