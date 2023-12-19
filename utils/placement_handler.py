import requests

from utils import constants
from utils.settings import open_file
from utils.game_requests import get_proxy_auth, get_request_strings

base_dimensions = 0.8


def calculate_placement(
    cap_id,
    raid,
    raid_id,
    cap_nm,
    name,
    user_id,
    token,
    user_agent,
    proxy,
    proxy_user,
    proxy_password,
    version,
    data_version,
):
    headers, proxies = get_request_strings(token, user_agent, proxy)
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_password)
    # Data on where units have been placed.
    gr_url = (
        "https://www.streamraiders.com/api/game/?cn=getRaid&userId="
        + user_id
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getRaid&raidId="
        + raid_id
        + "&maybeSendNotifs=False&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )
    getRaidJson = None
    if has_proxy:
        getRaidJson = requests.get(
            gr_url, proxies=proxies, headers=headers, auth=proxy_auth
        )
    else:
        getRaidJson = requests.get(gr_url, proxies=proxies, headers=headers)

    # Data on markers
    raidPlanJson = None
    r_url = (
        "https://www.streamraiders.com/api/game/?cn=getRaidPlan&userId="
        + user_id
        + "&isCaptain=0&gameDataVersion="
        + data_version
        + "&command=getRaidPlan&raidId="
        + raid_id
        + "&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )
    if has_proxy:
        raidPlanJson = requests.get(
            r_url, proxies=proxies, headers=headers, auth=proxy_auth
        )
    else:
        raidPlanJson = requests.get(r_url, proxies=proxies, headers=headers)

    # Data about the entire map.
    PlacementDataTxt = None
    pd_url = constants.mapPlacements + raid["battleground"] + ".txt"
    if has_proxy:
        PlacementDataTxt = requests.get(
            pd_url, proxies=proxies, headers=headers, auth=proxy_auth
        )
    else:
        PlacementDataTxt = requests.get(pd_url, proxies=proxies, headers=headers)
    getRaid = getRaidJson.json()
    raidPlan = raidPlanJson.json()
    MapData = PlacementDataTxt.json()

    if getRaid == None or raidPlan == None or MapData == None:
        print(
            f"Account {name}: something went wrong while trying to get placement data"
        )
        return

    ## Using the raid, raid plan and map data calculate placement

    # Have no clue how to get the dimensions of some of these sprites.
    # obstacles_coors = MapData["ObstaclePlacementData"]

    # Cortesy of project bots, they used the empiric method of trial and error so I didn't have to.
    map_scale = MapData["MapScale"]
    if map_scale < 0:
        map_width = MapData["GridWidth"]
        map_length = MapData["GridLength"]
    else:
        map_width = round(41 * map_scale)
        map_length = round(29 * map_scale)

    
    # Check if a battle map was initialized, then calculate positions and dimensions
    raidPlan = raidPlan["data"]
    if raidPlan is None:
        available_markers = {}
    else:
        available_markers = process_markers(raidPlan, map_width, map_length)

    # Units, allies, neutrals across the map
    h_units = getRaid["data"]["placements"]
    ai_units = MapData["PlacementData"]
    # Units, enemies and allies all have the same properties, so they can be merged together for processing
    all_units = h_units + ai_units
    map_units = open_file(constants.map_units_path)

    # Get units dimensions based on a list. Find captain coordinates
    for unit in all_units:
        unit_name = unit["CharacterType"]

        for key, units in map_units.items():
            if key == unit_name:
                is_epic = units["IsEpic"]
                cube_dimension = units["Size"]
                unit["IsEpic"] = is_epic
                if is_epic:
                    pass
                    # cube_dimension = cube_dimension * 2

                unit["width"] = cube_dimension
                unit["height"] = cube_dimension
                if unit["userId"] == cap_id:
                    cap_coors = {
                        "x": unit["X"],
                        "y": unit["Y"],
                        "width": 1.1,
                        "height": 1.1,
                    }
                break

        # Modify keys in all_units
        unit["x"] = unit.pop("X")
        unit["y"] = unit.pop("Y")

    # Draw imaginary map

    # Map tiles
    viewer_zones = MapData["PlayerPlacementRects"]
    purple_zones = MapData["HoldingZoneRects"]
    ally_zones = MapData["AllyPlacementRects"]
    enemy_zones = MapData["EnemyPlacementRects"]
    neutral_zones = MapData["NeutralPlacementRects"]

    # There's probably a cleaner way of doing this.
    a = [item for item in all_units]
    v = [item for item in viewer_zones]
    p = [item for item in purple_zones]
    ally = [item for item in ally_zones]
    e = [item for item in enemy_zones]
    n = [item for item in neutral_zones]

    dict_of_coors = {
        "all_units": a,
        "viewer": v,
        "purple": p,
        "ally": ally,
        "enemy": e,
        "neutral": n,
        "captain": cap_coors,
    }

    if available_markers is not None or available_markers is not {}:
        for marker_name, marker_data in available_markers.items():
            dict_of_coors[marker_name] = marker_data
    
    #For testing
    if cap_nm == "thecaptainscaptain":
        print(cap_nm)
        print(dict_of_coors)



def process_markers(raidPlan, map_width, map_length):
    # Check if there are markers
    markers = raidPlan["planData"]
    if markers is not None and "NoPlacement" in markers:
        del markers["NoPlacement"]
    if markers is None:
        return []

    dict_of_markers = {}
    for key, values in markers.items():
        temp_list = []

        for i in range(0, len(values) - 1, 2):
            entry = {
                "x": (float(values[i]) - float(map_width) / 2.0) * 0.8,
                "y": (float(map_length) / 2.0 - (float(values[i + 1]))) * 0.8,
                "width": base_dimensions, 
                "height": base_dimensions,
            }
            
            temp_list.append(entry)

        # Store the list of entries for each key in the dictionary
        dict_of_markers[key] = temp_list

    return dict_of_markers