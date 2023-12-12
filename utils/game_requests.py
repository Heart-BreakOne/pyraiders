import requests
from utils import constants


# Pass the headers and proxy formatted strings so requests can be performed.
def get_request_strings(token, user_agent, proxy):
    headers = {"Cookie": "ACCESS_INFO=" + token, "User-Agent": user_agent}
    proxies = {"http": "http://" + proxy}

    return headers, proxies


# Get each user's units, append priority and levelup permissions to each unit
def get_units_data(userId, token, user_agent, proxy, version, data_version):
    url = (
        constants.gameDataURL
        + "?cn=getUserUnits&userId="
        + userId
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getUserUnits&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )

    headers, proxies = get_request_strings(token, user_agent, proxy)

    response = requests.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        units = response.json().get("data", [])
        for each_unit in units:
            if each_unit["unitType"] == "alliesballoonbuster":
                each_unit["priority"] = 0
            else:
                each_unit["priority"] = 1
            each_unit["level_up"] = False
            # add an integer key called priority to each item before saving
    return units


# Get the game version and data_version for the api calls
def get_game_data():
    gameDataResponse = requests.get(constants.gameDataURL)
    # Check if the request was successful (status code 200)
    if gameDataResponse.status_code == 200:
        # Print the response content
        response_json = gameDataResponse.json()

        # Extract version from the JSON response
        # Version which goes in the clientVersion command. _shrug_
        version = response_json["info"]["version"]
        data_version = response_json["info"]["dataVersion"]
        return version, data_version
    else:
        return False, False


# Get userId and a list of favorite captains
def get_user_id(token, user_agent, proxy, version, data_version):
    url = (
        constants.gameDataURL
        + "?cn=getUser&gameDataVersion="
        + data_version
        + "&command=getUser&skipDataCheck=true&isLogin=true&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )

    headers, proxies = get_request_strings(token, user_agent, proxy)

    response = requests.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        parsedResponse = response.json()
        userId = parsedResponse["data"]["userId"]
        try:
            favoriteCaptains = parsedResponse["data"]["favoriteCaptainIds"]
        except KeyError:
            favoriteCaptains = ""
    return userId, favoriteCaptains


# Get userId, favorite captains and call to get the user units
def set_user_data(account_data):
    version, data_version = get_game_data()

    for account in account_data:
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]

        userId, favoriteCaptainIds = get_user_id(
            token, user_agent, proxy, version, data_version
        )
        account["userId"] = userId
        account["favoriteCaptainIds"] = favoriteCaptainIds

        account["has_pass"] = get_battlepass(
            userId, token, user_agent, proxy, version, data_version
        )
        if account["units"] == "":
            units = get_units_data(
                userId, token, user_agent, proxy, version, data_version
            )
            account["units"] = units
        else:
            # TODO Update unit level as the data already exists
            pass

    return account_data


def get_battlepass(userId, token, user_agent, proxy, version, data_version):
    url = (
        constants.gameDataURL
        + "?cn=getUserEventProgression&userId="
        + userId
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getUserEventProgression&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )

    headers, proxies = get_request_strings(token, user_agent, proxy)

    response = requests.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        parsedResponse = response.json()
        data = parsedResponse["data"]
        if data == None:
            return False
        
        for each in data:
            if each["eventUid"] == "snowfall_02":
                has_pass = each["hasBattlePass"]
                break
        if has_pass == "1":
            return True
        else:
            return False
