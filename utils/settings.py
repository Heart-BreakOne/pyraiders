import json, random
from utils import constants

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