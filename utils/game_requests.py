import requests
from utils import constants
from requests.auth import HTTPProxyAuth


# Pass the headers and proxy formatted strings so requests can be performed.
def get_request_strings(token, user_agent, proxy):
    headers = {"Cookie": "ACCESS_INFO=" + token, "User-Agent": user_agent}
    proxies = {"http": "http://" + proxy}
    return headers, proxies

def get_proxy_auth(proxy_user, proxy_pass):
    if proxy_user and proxy_pass:
        proxy_auth = HTTPProxyAuth(proxy_user, proxy_pass)
        return True, proxy_auth
    else:
        return False, ""


# Get each user's units, append priority and levelup permissions to each unit
def get_units_data(userId, token, user_agent, proxy, version, data_version, proxy_user, proxy_password):
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
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    if has_proxy:
        response = requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
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
def get_game_data(token, user_agent, proxy, proxy_user, proxy_password):
    
    _, proxies = get_request_strings(token, user_agent, proxy)
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    headers = {"User-Agent": user_agent}
    
    if has_proxy:
        gameDataResponse = requests.get(constants.gameDataURL, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        gameDataResponse = requests.get(constants.gameDataURL, proxies=proxies, headers=headers)

    # Check if the request was successful (status code 200)
    if gameDataResponse.status_code == 200:
        response_json = gameDataResponse.json()

        # Extract version from the JSON response
        # Version which goes in the clientVersion command. _shrug_
        version = response_json["info"]["version"]
        data_version = response_json["info"]["dataVersion"]
        return version, data_version
    else:
        return False, False


# Get userId and a list of favorite captains
def get_user_id(token, user_agent, proxy, version, data_version, proxy_user, proxy_password):
    url = (
        constants.gameDataURL
        + "?cn=getUser&gameDataVersion="
        + data_version
        + "&command=getUser&skipDataCheck=true&isLogin=true&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )

    headers, proxies = get_request_strings(token, user_agent, proxy)

    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    if has_proxy:
        response = requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        response = requests.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        parsedResponse = response.json()
        userId = parsedResponse["data"]["userId"]
        try:
            favoriteCaptains = parsedResponse["data"]["favoriteCaptainIds"]
        except KeyError:
            favoriteCaptains = ""
        try:
            other_user_id = parsedResponse["data"]["otherUserId"]
        except KeyError:
            other_user_id = ""
            
    return userId, other_user_id, favoriteCaptains


# Get userId, favorite captains and call to get the user units
def set_user_data(account_data):
    

    for account in account_data:
        if account["powered_on"] == False:
            continue

        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        proxy_user = account["proxy_user"]
        proxy_password = account["proxy_password"]
        
        version, data_version = get_game_data(token, user_agent, proxy, proxy_user, proxy_password)

        userId, other_user_id, favoriteCaptainIds = get_user_id(
            token, user_agent, proxy, version, data_version, proxy_user, proxy_password
        )
        account["userId"] = userId
        account["otherUserId"] = other_user_id
        account["favoriteCaptainIds"] = favoriteCaptainIds

        account["has_pass"] = get_battlepass(
            userId, token, user_agent, proxy, version, data_version, proxy_user, proxy_password
        )
        if account["units"] == "":
            units = get_units_data(
                userId, token, user_agent, proxy, version, data_version, proxy_user, proxy_password
            )
            account["units"] = units
        else:
            # TODO Update unit level as the data already exists
            pass

    return account_data


def get_battlepass(userId, token, user_agent, proxy, version, data_version, proxy_user, proxy_password):
    url = (
        constants.gameDataURL
        + "?cn=getEventProgressionLite&userId="
        + userId
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getEventProgressionLite&clientVersion="
        + version
        + "&clientPlatform=MobileLite"
    )

    headers, proxies = get_request_strings(token, user_agent, proxy)
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    if has_proxy:
        response = requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        response = requests.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        parsedResponse = response.json()
        data = parsedResponse["data"]
        if data == None:
            return False
        
        has_pass = data["hasBattlePass"]
        if has_pass == "1":
            return True
        else:
            return False
