import asyncio, requests
from datetime import datetime, timedelta
from utils.time_generator import get_four_quarters, get_quarter
from utils.settings import open_file, write_file
from utils.game_requests import get_request_strings, get_game_data, get_proxy_auth
from utils import constants


async def fill_slots():
    while True:
        await asyncio.sleep(get_quarter())
        # Fill empty slots.
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
            switch_if_preserve_loyalty = account["switch_if_preserve_loyalty"]
            switch_on_idle = account["switch_on_idle"]
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
            slots_quantity = account["slots"]

            activeRaids = getActiveraids(
                user_id, token, user_agent, proxy, proxy_user, proxy_password
            )
            # There are empty slots
            if (
                (has_pass and len(activeRaids) != 4)
                or (not has_pass and len(activeRaids) != 3)
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
                    has_pass,
                    slots_quantity,
                    preserve_loyalty,
                    switch_if_preserve_loyalty,
                    switch_on_idle,
                    minimum_idle_time,
                )
                continue
            else:
                # All slots are full, checks slots, place units
                place_units(
                    user_id,
                    token,
                    user_agent,
                    proxy,
                    proxy_user,
                    proxy_password,
                    preserve_loyalty,
                    switch_if_preserve_loyalty,
                    switch_on_idle,
                    minimum_idle_time,
                )
                continue

def getActiveraids(user_id, token, user_agent, proxy, proxy_user, proxy_password):
    headers, proxies = get_request_strings(token, user_agent, proxy)
    _, data_version = get_game_data(
        token, user_agent, proxy, proxy_user, proxy_password
    )
    url = (
        constants.gameDataURL
        + "?cn=getActiveRaidsByUser&userId="
        + user_id
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&clientPlatform:WebGL&command=getActiveRaidsByUser"
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
                {
                    "raidId": raidId,
                    "captainId": captainId,
                    "userSortIndex": userSortIndex,
                    "twitchUserName": twitchUserName,
                    "lastUnitPlacedTime": lastUnitPlacedTime,
                    "startTime": startTime,
                    "nodeId": nodeId,
                    "type": type,
                    "battleground": battleground,
                }
            )
        return activeRaids


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
    has_pass,
    slots_quantity,
    preserve_loyalty,
    switch_if_preserve_loyalty,
    switch_on_idle,
    minimum_idle_time,
):
    # Get list of active captains, filter it with the masterlist, favoriteCaptainsIds, blacklist
    live_captains_list = []
    headers, proxies = get_request_strings(token, user_agent, proxy)
    version, data_version = get_game_data(
        token, user_agent, proxy, proxy_user, proxy_password
    )
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
            response = requests.get(
                url, proxies=proxies, headers=headers, auth=proxy_auth
            )
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
            response = requests.get(
                url, proxies=proxies, headers=headers, auth=proxy_auth
            )
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

    # Clean up list to remove duplicate captains
    for entry in merged_data:
        id = entry["userId"]
        if id not in unique_user_ids:
            unique_user_ids.add(id)
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

    # Remove active captains from the live captains list
    active_captain_ids = set(entry["captainId"] for entry in activeRaids)
    acceptable_captains = [
        entry
        for entry in acceptable_captains
        if entry["userId"] not in active_captain_ids
    ]

    # Remove live captains that are running special modes that active captains are also running to avoid.
    active_types = {entry["type"] for entry in activeRaids if "type" in entry}
    acceptable_captains = [
        entry
        for entry in acceptable_captains
        if entry.get("type") == "1"
        or (
            entry.get("type")
            and set(entry["type"]) != {"1"}
            and set(entry["type"]) != active_types
        )
    ]

    # Remove captains that are on the temporary idle list for the last 30 minutes
    # Convert the time strings to datetime variables
    temporary_ignore_times = [
        datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S.%f")
        for entry in temporary_ignore
    ]

    current_time = datetime.now()
    # Define the threshold for acceptable captains (30 minutes)
    threshold_time = timedelta(minutes=30)
    # Filter out captains younger than 30 minutes in temporary_ignore
    captains_to_remove = [
        entry["capNm"].upper()
        for entry, time_entry in zip(temporary_ignore, temporary_ignore_times)
        if current_time - time_entry < threshold_time
    ]
    # Remove corresponding entries from acceptable_captains
    acceptable_captains = [
        entry
        for entry in acceptable_captains
        if entry["twitchUserName"].upper() not in captains_to_remove
    ]

    # The list left is ready to be used for placement, now figure out what slots are available
    # Initialize slots list
    slots = []
    for raid in activeRaids:
        slots.append(raid["userSortIndex"])
    possible_slots = []

    if has_pass and len(slots) != 4:
        possible_slots = list(set(["0", "1", "2", "3"]) - set(slots))

    elif not has_pass and len(slots) != 3:
        possible_slots = list(set(["0", "1", "2"]) - set(slots))

    # If possible_slots is not empty it means there are slots that can be filled up, fill them up the acceptable_captains list.
    if len(possible_slots) != 0:
        select_captain(
            user_id,
            headers,
            proxies,
            version,
            data_version,
            has_proxy,
            proxy_auth,
            possible_slots,
            acceptable_captains,
            token,
            user_agent,
            proxy,
            proxy_user,
            proxy_password,
            slots_quantity,
            preserve_loyalty,
            switch_if_preserve_loyalty,
            switch_on_idle,
            minimum_idle_time,
        )
    else:
        place_units(
            user_id,
            token,
            user_agent,
            proxy,
            proxy_user,
            proxy_password,
            preserve_loyalty,
            switch_if_preserve_loyalty,
            switch_on_idle,
            minimum_idle_time,
        )
        return


# Place captain on slot
def select_captain(
    user_id,
    headers,
    proxies,
    version,
    data_version,
    has_proxy,
    proxy_auth,
    possible_slots,
    acceptable_captains,
    token,
    user_agent,
    proxy,
    proxy_user,
    proxy_password,
    slots_quantity,
    preserve_loyalty,
    switch_if_preserve_loyalty,
    switch_on_idle,
    minimum_idle_time,
):
    for i, slot in enumerate(possible_slots):
        slot_integer = int(slot)
        if i < len(acceptable_captains) and slot_integer < slots_quantity:
            captain_id = acceptable_captains[i]["userId"]
            captain_name = acceptable_captains[i]["twitchUserName"]
        else:
            place_units(
                user_id,
                token,
                user_agent,
                proxy,
                proxy_user,
                proxy_password,
                preserve_loyalty,
                switch_if_preserve_loyalty,
                switch_on_idle,
                minimum_idle_time,
            )
            return

        url = (
            constants.gameDataURL
            + "?cn=addPlayerToRaid&userId="
            + user_id
            + "&isCaptain=0&gameDataVersion="
            + data_version
            + "&command=addPlayerToRaid&userSortIndex="
            + slot
            + "&captainId="
            + captain_id
            + "&clientVersion="
            + version
            + "&clientPlatform=WebGL"
        )
        if has_proxy:
            requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
            print(
                "Account:"
                + user_id
                + ". Added "
                + captain_name
                + " to slot number "
                + slot
            )
        else:
            requests.get(url, proxies=proxies, headers=headers)
            print(
                "Account:"
                + user_id
                + ". Added "
                + captain_name
                + " to slot number "
                + slot
            )

    # get active raids again and count the occupied slots, that is the real amount of slots
    activeRaids = getActiveraids(
        user_id, token, user_agent, proxy, proxy_user, proxy_password
    )
    real_slot_quantity = len(activeRaids)
    accounts = open_file(constants.py_accounts)
    for account in accounts:
        if account["userId"] == user_id or account["otherUserId"] == user_id:
            account["slots"] = real_slot_quantity

    write_file(constants.py_accounts, accounts)


# Check idle captains and loyalty switch.
def place_units(
    user_id,
    token,
    user_agent,
    proxy,
    proxy_user,
    proxy_password,
    preserve_loyalty,
    switch_if_preserve_loyalty,
    switch_on_idle,
    minimum_idle_time,
):
    #Once again, get active raids
    activeRaids = getActiveraids(
        user_id, token, user_agent, proxy, proxy_user, proxy_password
    )
    
    #Remove idle captains from the slots.
    if switch_on_idle:
        for raid in activeRaids:
            print(raid)
    
    print("TODO - CLEAN IDLE CAPTAINS AND LOYALTY CAPTAINS")
    # Get active raids.
    # Check captains running on loyalty switch
    # Check captains idling
