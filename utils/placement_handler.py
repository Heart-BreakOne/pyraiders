import time, requests
from datetime import datetime
from utils import constants
from utils.game_requests import (
    check_potions,
    equip_skin,
    get_live_captains,
    get_proxy_auth,
    get_request_strings,
)
from utils.logger import log_to_file
from utils.settings import check_raid_type, validate_raid


# OFFSET AN EPIC UNIT BEFORE PLACING IT BY ADDING +0.4
def place_the_unit(
    can_epic,
    raid,
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
    can_epic = False
    is_epic = False
    log_to_file(f"log-placement Starting placement handler for {name} at {cap_nm}")
    def place(unit, marker, is_epic):
        log_to_file(f"log-placement Attempting placement for unit {unit} at marker {marker}")
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
        if is_epic:
            print("Epic placement")
            epic = "epic"
        else:
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
        
        # Check if user wants to equip a skin
        skin = equip_skin(user_id, version, data_version, token, user_agent, proxy, proxy_user, proxy_password, unitName, cap_nm, skin)
        log_to_file(f"log-placement Skin is {skin}")
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

        # Check raid state
        headers, proxies = get_request_strings(token, user_agent, proxy)
        has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)

        merged_data = get_live_captains(
            name, headers, proxies, version, data_version, has_proxy, proxy_auth
        )
        for captain in merged_data:
            if (
                captain["twitchUserName"].lower() == cap_nm.lower()
                and captain["raidState"] != 4
            ):
                return 3

        # Get new raid and recalculate
        # Check if raid is in valid placement
        now = datetime.utcnow()
        if not validate_raid(raid):
            return 3

        time_difference = now - creation_time
        if not check_raid_type(raid_type, time_difference):
            return 3

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
                pr_str = f"Account {name}: {unitName} with skin {skin} placed successfully at {cap_nm} at {now}"
                print(pr_str)
                log_to_file(pr_str)
                return 0
            else:
                time.sleep(5)
                # INVALID_RAID_STATE:5 = Battle ready soon. View Battlefield
                if "INVALID_RAID_STATE" in errorMsg or errorMsg == "PERIOD_ENDED":
                    pr_str = f"Account {name}: Placement failed due to {errorMsg} on captain {cap_nm}"
                    log_to_file(pr_str)
                    print(pr_str)
                    return 3
                elif errorMsg == "OVER_UNIT" or errorMsg == "OVER_ENEMY":
                    pr_str = f"Account {name}: Placement failed due to {errorMsg} on captain {cap_nm}"
                    log_to_file(pr_str)
                    # print(pr_str)
                    return 2
                else:
                    pr_str = f"Account {name}: Placement failed due to {errorMsg} on captain {cap_nm}"
                    log_to_file(pr_str)
                    print(pr_str)
                    return 2
        else:
            pr_str = f"Account {name}: Placement request failed with status code: {response.status_code} on captain {cap_nm}. URL: {url}"
            print(pr_str)
            return 1

    # The markers work for the unit, not the units for the marker.
    attempt = 0

    for unit in units:
        if attempt == 30:
            break
        for marker in usable_markers:
            if attempt == 30:
                break
            marker_type = marker["type"].lower()
            # Find marker that matches the unit
            if marker_type == "vibe":
                if can_epic:
                    is_epic, marker = calculate_epic_marker(
                        marker,
                        usable_markers,
                        user_id,
                        data_version,
                        version,
                        token,
                        user_agent,
                        proxy,
                        proxy_user,
                        proxy_password,
                    )
                # Marker fits anything, place the unit
                has_placed = place(unit, marker, is_epic)
                if has_placed == 0:
                    log_to_file(f"log-placement Vibe Placemenet sucessful")
                    attempt = 30
                    break
                elif has_placed == 3:
                    log_to_file(f"log-placement Vibe Placement failed")
                    attempt = 30
                    break
                else:
                    log_to_file(f"log-placement Vibe Trying new placement")
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
                        if can_epic:
                            is_epic, marker = calculate_epic_marker(
                                marker,
                                usable_markers,
                                user_id,
                                data_version,
                                version,
                                token,
                                user_agent,
                                proxy,
                                proxy_user,
                                proxy_password,
                            )
                        has_placed = place(unit, marker, is_epic)
                        if has_placed == 0:
                            log_to_file(f"log-placement Placement sucessful")
                            attempt = 30
                            break
                        elif has_placed == 3:
                            log_to_file(f"log-placement Placement failed")
                            attempt = 30
                            break
                        else:
                            log_to_file(f"log-placement Trying new placement")
                            attempt += 1


def calculate_epic_marker(
    marker,
    usable_markers,
    user_id,
    data_version,
    version,
    token,
    user_agent,
    proxy,
    proxy_user,
    proxy_password,
):
    return False, marker

    # Check if user has enough potions to use
    has_potions = check_potions(
        user_id,
        data_version,
        version,
        token,
        user_agent,
        proxy,
        proxy_user,
        proxy_password,
    )

    if not has_potions:
        return False, marker

    backup_marker = marker

    # User has potions, find 3 other markers that are in a square formation to my current marker
    def quadrant(coord):
        if coord["x"] >= 0 and coord["y"] >= 0:
            return 1
        elif coord["x"] < 0 and coord["y"] >= 0:
            return 2
        elif coord["x"] < 0 and coord["y"] < 0:
            return 3
        else:
            return 4

    def filter_markers(markers, quad):
        return [m for m in markers if quadrant(m) == quad]

    marker_quad = quadrant(marker)

    quadrants_234_markers = (
        filter_markers(usable_markers, 2)
        + filter_markers(usable_markers, 3)
        + filter_markers(usable_markers, 4)
    )

    if marker_quad == 1:
        marker["x"] = marker["x"] - 0.4
        marker["y"] = marker["y"] - 0.4
        return True, marker

    if not quadrants_234_markers:
        return False, backup_marker

    return False, backup_marker
