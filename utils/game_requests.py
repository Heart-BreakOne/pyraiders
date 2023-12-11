import requests
from utils.settings import open_file
from utils import constants


#Pass the headers and proxy strings so requests can be performed.
def get_request_strings(token, user_agent, proxy):
    headers = {"Cookie": "ACCESS_INFO=" + token, "User-Agent": user_agent}
    proxies = {"http": "http://" + proxy}
    
    return headers, proxies
    
    
def get_variables():
    settings_data = open_file(constants.py_captain)
    version = settings_data.get("version", {})
    data_version = settings_data.get("data_version", {})
    userId = settings_data.get("userId", {})
    access_info = settings_data.get("access_info", {})
    user_agent = settings_data.get("user_agent", {})
    headers = {"Cookie": "ACCESS_INFO=" + access_info, "User-Agent": user_agent}
    return {
        "version": version,
        "data_version": data_version,
        "userId": userId,
        "headers": headers,
    }


def get_display_data():
    variables = get_variables()
    url = (
        "https://www.streamraiders.com/api/game/?cn=getAvailableCurrencies&userId="
        + str(variables["userId"])
        + "&isCaptain=1&gameDataVersion="
        + str(variables["data_version"])
        + "&command=getAvailableCurrencies&clientVersion="
        + str(variables["version"])
        + "&clientPlatform=WebGL"
    )
    response = requests.get(url, headers=variables["headers"])
    if response.status_code == 200:
        return response.json()


# Get each user's units, append priority and levelup permissions to each unit
def get_units_data(userId, token, user_agent, proxy, version, data_version):
    url = (
        "https://www.streamraiders.com/api/game/?cn=getUserUnits&userId="
        + userId
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getUserUnits&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )
    
    headers, proxies = get_request_strings(token, user_agent, proxy)

    response = requests.get(
        url, proxies=proxies, headers=headers
    )
    if response.status_code == 200:
        units = response.json().get("data", [])
        for each_unit in units:
            print(each_unit)
            if each_unit["unitType"] == "alliesballoonbuster":
                each_unit["priority"] = 0
            else:
                each_unit["priority"] = 1
            each_unit["level_up"] = False
            # add an integer key called priority to each item before saving
    return units


# Get the game versino and data_version for the api calls
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


#Get userId and a list of favorite captains
def get_user_id(token, user_agent, proxy, version, data_version):
    url = (
        "https://www.streamraiders.com/api/game/?cn=getUser&gameDataVersion="
        + data_version
        + "&command=getUser&skipDataCheck=true&isLogin=true&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )
    
    headers, proxies = get_request_strings(token, user_agent, proxy)

    response = requests.get(
        url, proxies=proxies, headers=headers
    )
    if response.status_code == 200:
        parsedResponse = response.json()
        userId = parsedResponse["data"]["userId"]
        try:
            favoriteCaptains = parsedResponse["data"]["favoriteCaptainIds"]
        except KeyError:
            favoriteCaptains = ""
    return userId, favoriteCaptains


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

        if account["units"] == "":
            units = get_units_data(
                userId, token, user_agent, proxy, version, data_version
            )
            account["units"] = units
        else:
            # TODO Update unit level as the data already exists
            pass

    return account_data