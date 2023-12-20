import time, requests
from datetime import datetime
from utils import constants
from utils.game_requests import get_proxy_auth, get_request_strings
from utils.settings import check_raid_type, validate_raid


# OFFSET AN EPIC UNIT BEFORE PLACING IT BY ADDING +0.4
def place_the_unit(
    units,
    usable_markers,
    cap_nm,
    raid_id,
    name,
    user_id,
    token,
    user_agent,
    proxy,
    proxy_user,
    proxy_password,
    version,
    data_version,
    previous_placement,
    raid_type,
    creation_time,
):
    def place(unit, marker):
        for d_unit in constants.units_dict:
            if (
                unit["unitType"].lower() == d_unit["name"].lower()
                or unit["unitType"].lower() == d_unit["alt"].lower()
                or unit["unitType"] == d_unit["type"].lower()
            ):
                unitName = d_unit["name"].lower()
                break

        x = str(marker["x"])
        y = str(marker["y"])
        epic = ""
        unitLevel = unit["level"]
        unitId = unit["unitId"]

        soulType = unit["soulType"]
        specializationUid = unit["specializationUid"]
        skin = unit["skin"]
        if soulType == None:
            soulType = ""
        if specializationUid == None:
            specializationUid = ""
        if skin == None:
            skin = ""

        url = (
            constants.gameDataURL
            + "?cn=addToRaid&raidId="
            + raid_id
            + '&placementData={"userId":"'
            + user_id
            + '","CharacterType":"'
            + epic
            + unitName
            + unitLevel
            + '","SoulType":"'
            + soulType
            + '","X":"'
            + x
            + '","Y":"'
            + y
            + '","skin":"'
            + skin
            + '","specializationUid":"'
            + specializationUid
            + '","unitId":"'
            + unitId
            + '","stackRaidPlacementsId":0,"team":"Ally","onPlanIcon":false}&clientVersion='
            + version
            + "&clientPlatform=WebGL&gameDataVersion="
            + data_version
            + "&command=addToRaid&isCaptain=0"
        )
        # Check if raid is in valid placement
        now = datetime.utcnow()
        if not validate_raid(previous_placement, now, raid_type, creation_time):
            return
        
        time_difference = now - creation_time
        if not check_raid_type(raid_type, time_difference):
            return
        
        headers, proxies = get_request_strings(token, user_agent, proxy)
        has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
        if has_proxy:
            response = requests.get(
                url, proxies=proxies, headers=headers, auth=proxy_auth
            )
        else:
            response = requests.get(url, proxies=proxies, headers=headers)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            errorMsg = data.get("errorMessage")
            if status == "success" and errorMsg == None:
                now = datetime.now().strftime("%H:%M:%S")
                print(
                    "Account: "
                    + name
                    + " "
                    + unitName
                    + " placed successfully at "
                    + cap_nm
                    + " at "
                    + now
                )
                return True
            else:
                time.sleep(5)
                if errorMsg == "OVER_UNIT":
                    print("Placement failed due to " + errorMsg)
                    return False
                print("Placement failed due to " + errorMsg)
                print(url)
                print(marker)
                print(unitName)
                return False
        else:
            print(f"Placement request failed with status code: {response.status_code}")
            print(url)
            print(marker)
            print(unitName)
            return False

    # The markers work for the unit, not the units for the marker.
    attempt = 0

    for unit in units:
        for marker in usable_markers:
            marker_type = marker["type"].lower()
            # Find marker that matches the unit
            if marker_type == "vibe":
                # Marker fits anything, place the unit
                has_placed = place(unit, marker)
                if has_placed:
                    attempt = 10
                    break
                else:
                    attempt += 1

            else:
                # Check if current marker matches the unit
                # get unit actual name from the list as well as the unit type
                u_nm = unit["unitType"].lower()
                unit_name = ""
                unit_type = ""
                for d_unit in constants.units_dict:
                    ud_name = d_unit["name"].lower()
                    ud_alt = d_unit["alt"].lower()
                    ud_type = d_unit["type"].lower()
                    if u_nm == ud_name or u_nm == ud_alt or u_nm == ud_type:
                        unit_name = d_unit["name"]
                        unit_type = d_unit["type"]
                    if marker_type == unit_name or marker_type == unit_type:
                        has_placed = place(unit, marker)
                        if has_placed:
                            attempt = 10
                            break
                        else:
                            attempt += 1
        if attempt == 10:
            break