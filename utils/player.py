import asyncio, requests
from utils.time_generator import get_four_quarters, get_quarter
from utils.settings import open_file
from utils.game_requests import get_request_strings, get_game_data, get_proxy_auth
from utils import constants


async def play():
    while True:
        await asyncio.sleep(get_quarter())

        # Two tasks to perform in here

        # Fill empty slots.
        fill_slots()
        # Place units.


def fill_slots():
    accounts = open_file(constants.py_accounts)
    for account in accounts:
        # Check if account is running
        if account["powered_on"] == False:
            continue
        # Required data
        user_id = account["userId"]
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        proxy_user = account["proxy_user"]
        proxy_password = account["proxy_password"]

        # Data for the conditional checks
        preserve_loyalty = account["preserve_loyalty"]
        switch_if_no_loyalty = account["switch_if_no_loyalty"]
        switch_on_idle = account["switch_on_idle"]
        if switch_on_idle:
            minimum_idle_time = account["minimum_idle_time"]
        unlimited_campaign = account["unlimited_campaign"]
        unlimited_pvp = account["unlimited_pvp"]
        only_masterlist = account["only_masterlist"]
        masterlist = []
        if only_masterlist:
            masterlist = account["masterlist"]
        ignore_blacklist = account["ignore_blacklist"]
        blacklist = []
        if ignore_blacklist:
            blacklist = account["blacklist"]
        favorites_only = account["favorites_only"]
        favoriteCaptainIds = []
        if favorites_only:
            favoriteCaptainIds = account["favoriteCaptainIds"]
        any_captain = account["any_captain"]
        temporary_ignore = account["temporary_ignore"]
        has_pass = account["has_pass"]

        activeRaids = getActiveraids(user_id, token, user_agent, proxy, proxy_user, proxy_password)
        # There are empty slots
        if (
            (has_pass and len(activeRaids) != 4)
            or (not has_pass and len(activeRaids) != 4)
            or activeRaids == None
            or activeRaids == []
        ):
            fill_empty_slots(
                activeRaids,
                user_id,
                token,
                user_agent,
                proxy,
                proxy_user,
                proxy_password,
                temporary_ignore,
                masterlist,
                favoriteCaptainIds,
                blacklist,
                any_captain,
            )
            continue
        else:
            # All slots are filled, check if slot should be replace or if an unit should be placed
            pass

    # Task 3 -> Place available greenlighted captains based on the ruleset on any slots that may be available.
    # Task 4 -> Flag captains that may be idling.
    # Task 5 -> Check if there greenlighted captains and if there idling captains. Replace them.

    # TODO fill slots
    pass


def place_units():
    # TODO place units
    pass


def getActiveraids(user_id, token, user_agent, proxy, proxy_user, proxy_password):
    headers, proxies = get_request_strings(token, user_agent, proxy)
    _, data_version = get_game_data(token, user_agent, proxy, proxy_user, proxy_password)
    url = (
        constants.gameDataURL
        + "?cn=getActiveRaidsByUser&userId="
        + user_id
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getActiveRaidsByUser"
    )
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    if has_proxy:
        response = requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        response = requests.get(url, proxies=proxies, headers=headers)
    if response.status_code == 200:
        parsedResponse = response.json()
        raid_data = parsedResponse["data"]
        activeRaids = []
        if raid_data == None:
            return activeRaids.append("all slots are empty")
        occupied_slots = len(raid_data)

        for raid in raid_data:
            raidId = raid["raidId"]
            if raidId == None:
                continue
            captainId = raid["captainId"]
            userSortIndex = raid["userSortIndex"]
            twitchUserName = raid["twitchUserName"]
            lastUnitPlacedTime = raid["lastUnitPlacedTime"]
            startTime = raid["startTime"]
            nodeId = raid["nodeId"]
            type = raid["type"]
            battleground = raid["battleground"]
            activeRaids.append(
                (
                    raidId,
                    captainId,
                    userSortIndex,
                    twitchUserName,
                    lastUnitPlacedTime,
                    startTime,
                    nodeId,
                    type,
                    battleground,
                )
            )
        return activeRaids, occupied_slots


def fill_empty_slots(
    activeRaids,
    user_id,
    token,
    user_agent,
    proxy,
    proxy_user,
    proxy_password,
    temporary_ignore,
    masterlist,
    favoriteCaptainIds,
    blacklist,
    any_captain,
):

    # Get list of active captains, filter it with the masterlist, favoriteCaptainsIds, blacklist
    live_captains_list = []
    headers, proxies = get_request_strings(token, user_agent, proxy)
    version, data_version = get_game_data(token, user_agent, proxy, proxy_user, proxy_password)
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    for i in range(6):
        url = (
            constants.gameDataURL
            + "?cn=getCaptainsForSearch&isPlayingS=desc&isLiveS=desc&page="
            + str(i)
            + "&format=normalized&seed=0&resultsPerPage=30&filters=%7B%22favorite%22%3Afalse%2C%22isLive%22%3A1%2C%22ambassadors%22%3A%22false%22%7D&clientVersion="
            + version
            + "&clientPlatform=WebGL&gameDataVersion="
            + data_version
            + "&command=getCaptainsForSearch&isCaptain=0"
        )
        if has_proxy:
            response = requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
        else:
            response = requests.get(url, proxies=proxies, headers=headers)
        live_captains_list.append(response.json())

    for i in range(3):
        url = (
            constants.gameDataURL
            + "?cn=getCaptainsForSearch&isPlayingS=desc&isLiveS=desc&page="
            + str(i)
            + "&format=normalized&seed=0&resultsPerPage=30&filters=%7B%22favorite%22%3Atrue%2C%22isLive%22%3A1%2C%22ambassadors%22%3A%22false%22%7D&clientVersion="
            + version
            + "&clientPlatform=WebGL&gameDataVersion="
            + data_version
            + "&command=getCaptainsForSearch&isCaptain=0"
        )
        if has_proxy:
            response = requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
        else:
            response = requests.get(url, proxies=proxies, headers=headers)
        live_captains_list.append(response.json())

    merged_data = []
    captains_data_list = [entry["data"]["captains"] for entry in live_captains_list]
    merged_data = [
        captain for captains_data in captains_data_list for captain in captains_data
    ]

    unique_user_ids = set()
    unique_data = []

    for entry in merged_data:
        user_id = entry["userId"]
        if user_id not in unique_user_ids:
            unique_user_ids.add(user_id)
            unique_data.append(entry)

    acceptable_captains = []
    # User wants to use masterlist
    if len(masterlist) != 0:
        acceptable_captains = sorted(
            (
                entry
                for entry in unique_data
                if entry["twitchUserName"].upper() in map(str.upper, masterlist)
            ),
            key=lambda x: masterlist.index(x["twitchUserName"].upper())
            if x["twitchUserName"].upper() in masterlist
            else float("inf"),
        )

    # User wants favorite list
    if len(acceptable_captains) == 0 and favoriteCaptainIds != "":
        for entry in unique_data:
            captain = entry["userId"]
            if captain in favoriteCaptainIds:
                acceptable_captains.append(entry)

    if len(acceptable_captains) == 0 and len(blacklist) != 0 and any_captain:
        for entry in unique_data:
            captain = entry["twitchUserName"].upper()
            if captain in map(str.upper, blacklist):
                pass
            else:
                acceptable_captains.append(entry)

    if len(acceptable_captains) == 0 and any_captain:
        acceptable_captains = unique_data

    # Now that the list of usable live captains has been made, filter out active captains and avoid a duplicate pvp/dungeon captain
    print(acceptable_captains)
