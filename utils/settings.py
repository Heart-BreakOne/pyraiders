import json, random
from datetime import datetime, timedelta
import sys
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
    # Generate unique user agent
    def generate_unique_user_agent(existing_user_agents):
        base_user_agent = random.choice(constants.user_agents)
        new_user_agent = base_user_agent
        while new_user_agent in existing_user_agents:
            new_user_agent = base_user_agent
        existing_user_agents.add(new_user_agent)
        return new_user_agent

    # Generate unique proxy
    def generate_unique_proxy(existing_proxies):
        base_proxy = random.choice(constants.proxies)
        new_proxy = base_proxy
        while new_proxy in existing_proxies:
            new_proxy = base_proxy
        existing_proxies.add(new_proxy)
        return new_proxy

    # Set of existing values
    existing_user_agents = set()
    existing_proxies = set()
    existing_names = set()
    existing_tokens = set()

    unique_accounts = []

    # Clean up the data.
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
            if (
                account_data["user_agent"] == ""
                or account_data["user_agent"] in existing_user_agents
            ):
                account_data["user_agent"] = generate_unique_user_agent(
                    existing_user_agents
                )

            # Add proxy if empty, "none", or duplicate
            if (
                account_data["proxy"].lower() in ["none", ""]
                or account_data["proxy"] in existing_proxies
            ):
                account_data["proxy"] = generate_unique_proxy(existing_proxies)

            existing_names.add(account_data["name"])
            existing_tokens.add(account_data["token"])
            existing_user_agents.add(account_data["user_agent"])
            existing_proxies.add(account_data["proxy"])

            unique_accounts.append(account_data)

    return unique_accounts


# Add temporary ignore captains
def add_temporary_ignore(user_id, captain_name):
    accounts = open_file(constants.py_accounts)

    # Add captain to the temporary ignore list to avoid a loop switch
    for account in accounts:
        if account["userId"] == user_id or account["otherUserId"] == user_id:
            temporary_ignore = account.get("temporary_ignore", [])
            time = datetime.utcnow()
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            new_entry = {"capNm": captain_name, "time": current_time}
            temporary_ignore.append(new_entry)
            account["temporary_ignore"] = temporary_ignore

    write_file(constants.py_accounts, accounts)


# Remove temporary data that is older than 30 minutes
def clean_temp_times(accounts):
    for account in accounts:
        temp_ignore_list = account["temporary_ignore"]

        # Remove missing and empty values.
        try:
            temp_ignore_list = [
                entry for entry in temp_ignore_list if entry.get("time")
            ]
            temp_ignore_times = [
                datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
                for entry in temp_ignore_list
            ]

            time = datetime.utcnow()
            current_time = datetime.strptime(
                time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S"
            )

            threshold_time = timedelta(minutes=30)
            temp_ignore_list = [
                entry
                for entry, time_entry in zip(temp_ignore_list, temp_ignore_times)
                if current_time - time_entry < threshold_time
            ]

            account["temporary_ignore"] = temp_ignore_list

        except Exception as e:
            print(e)
            sys.exit()

    return accounts


# Remove accounts with duplicate user ids.
def remove_duplicate_ids(accounts):
    unique_ids = set()
    unique_accounts = []

    for account in accounts:
        user_id = account["userId"]
        alt_user_id = account["otherUserId"]
        units = account["units"]
        unit_ids = set()

        if (user_id, alt_user_id) not in unique_ids and (
            user_id,
            alt_user_id,
        ) not in unique_ids:
            unique_ids.add((user_id, alt_user_id))

            has_duplicate_units = False
            for unit in units:
                unit_id = unit["unitId"]
                if unit_id in unit_ids:
                    has_duplicate_units = True
                    break
                else:
                    unit_ids.add(unit_id)

            if not has_duplicate_units:
                unique_accounts.append(account)

    return unique_accounts


def validate_raid(previous_placement, now, raid_type, creation_time):
    if raid_type == "1":
        # Campaign
        time_since_creation = now - creation_time if creation_time else timedelta(0)
        time_since_previous_placement = (
            now - previous_placement if previous_placement else timedelta(minutes=6)
        )
        if (
            time_since_creation <= timedelta(minutes=1, seconds=30)
            or time_since_creation > timedelta(minutes=29, seconds=55)
            or time_since_previous_placement < timedelta(minutes=5)
        ):
            return False
    elif raid_type == "2" or raid_type == "5":
        time_since_creation = now - creation_time if creation_time else timedelta(0)
        time_since_previous_placement = (
            now - previous_placement if previous_placement else timedelta(minutes=2)
        )
        if (
            time_since_creation <= timedelta(minutes=1, seconds=5)
            or time_since_creation > timedelta(minutes=6, seconds=55)
            or time_since_previous_placement < timedelta(minutes=2, seconds=00)
        ):
            return False
    elif raid_type == "3":
        # Dungeons
        time_since_creation = now - creation_time if creation_time else timedelta(0)
        time_since_previous_placement = (
            now - previous_placement if previous_placement else timedelta(minutes=2)
        )
        if (
            time_since_creation <= timedelta(minutes=1, seconds=5)
            or time_since_creation > timedelta(minutes=5, seconds=55)
            or time_since_previous_placement < timedelta(minutes=1, seconds=40)
        ):
            return False
    return True


def check_raid_type(raid_type, time_difference):
    if raid_type == "1":
        # Campaign
        if time_difference > timedelta(minutes=29, seconds=50):
            return False
    elif raid_type == "2" or raid_type == "5":
        # Duels and clash
        if time_difference > timedelta(minutes=6, seconds=55):
            return False
    elif raid_type == "3":
        # Dungeons
        if time_difference > timedelta(minutes=5, seconds=55):
            return False

    return True
