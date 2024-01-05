import math
import random
import requests

from utils import constants
from utils.settings import open_file
from utils.game_requests import get_proxy_auth, get_request_strings

base_dimensions = 0.8


# "x" "y" "width" "height"
def calculate_placement(
    cap_id,
    raid,
    raid_id,
    name,
    cap_nm,
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
        constants.gameDataURL
        + "?cn=getRaid&userId="
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
        constants.gameDataURL
        + "?cn=getRaidPlan&userId="
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
            f"Account {name}: something went wrong while trying to get placement data at {cap_nm}"
        )
        return

    ## Using the raid, raid plan and map data calculate placement

    # Have no clue how to get the dimensions of some of these sprites.
    # obstacles_coors = MapData["ObstaclePlacementData"]

    # Cortesy of project bots, they used the empiric method of trial and error so I didn't have to.
    map_scale = MapData["MapScale"]
    if map_scale < 0:
        map_width = MapData["GridWidth"]
        map_height = MapData["GridLength"]
    else:
        map_width = round(41 * map_scale)
        map_height = round(29 * map_scale)

    # Check if a battle map was initialized, then calculate positions and dimensions
    raidPlan = raidPlan["data"]
    if raidPlan is None:
        available_markers = {}
    else:
        available_markers = process_markers(raidPlan, map_width, map_height)

    # Units, allies, neutrals across the map
    h_units = []
    ai_units = []
    try:
        h_units = getRaid["data"]["placements"]
        ai_units = MapData["PlacementData"]
    except:
        return []

    # Units, enemies and allies all have the same properties, so they can be merged together for processing
    all_units = h_units + ai_units
    map_units = open_file(constants.map_units_path)
    cap_coors = {}
    # Get units dimensions based on a list. Find captain coordinates
    for unit in all_units:
        unit_name = unit["CharacterType"]

        for key, units in map_units.items():
            if key == unit_name:
                try:
                    # General units across the map   #Offset epic units by minus 0.4
                    if units["IsEpic"]:
                        unit["width"] = units["Size"] * 2
                        unit["height"] = units["Size"] * 2
                        unit["X"] = float(unit["X"]) - 0.4
                        unit["Y"] = float(unit["Y"]) - 0.4
                    # Epic viewer units (default is always 0.8 so there's no need to get the value from units["Size"])
                    if "epic" in unit_name and unit["userId"] != "":
                        unit["width"] = 1.6
                        unit["height"] = 1.6
                        unit["X"] = float(unit["X"]) - 0.4
                        unit["Y"] = float(unit["Y"]) - 0.4
                    else:
                        unit["width"] = 0.8
                        unit["height"] = 0.8
                except Exception as e:
                    unit["width"] = units["Size"]
                    unit["height"] = units["Size"]
                # Grabbing captain to user later
                if unit["userId"] == cap_id:
                    cap_coors = {
                        "x": float(unit["X"]),
                        "y": float(unit["Y"]),
                        "width": 1.6,
                        "height": 1.6,
                    }
                continue

        # Modify keys in all_units
        unit["x"] = unit.pop("X")
        unit["y"] = unit.pop("Y")

    # Draw imaginary map
    # Map tiles
    # enemy_zones = MapData["EnemyPlacementRects"]
    viewer_squares = make_imaginary_mkrs(MapData["PlayerPlacementRects"])
    purple_squares = make_imaginary_mkrs(MapData["HoldingZoneRects"])
    ally_squares = make_imaginary_mkrs(MapData["AllyPlacementRects"])
    # No longer to be found on the MapData file
    # neutral_squares = make_imaginary_mkrs(MapData["NeutralPlacementRects"])
    # m_list.extend(neutral_squares)
    # f_neutral_squares = remove_overlap(neutral_squares, m_list)

    m_list = []
    m_list.extend(all_units)
    m_list.extend(ally_squares)
    m_list_no_purple = m_list
    m_list.extend(purple_squares)

    f_viewer_squares = remove_overlap(viewer_squares, m_list)
    f_purple_squares = remove_overlap(purple_squares, m_list_no_purple)

    markers = []
    if available_markers is not None or available_markers is not {}:
        for marker_name, marker_data in available_markers.items():
            if isinstance(marker_data, list):
                for single_marker_data in marker_data:
                    if not isinstance(single_marker_data, dict):
                        print(
                            f"Unexpected data type found for {marker_name}: {type(single_marker_data)}"
                        )
                        continue

                    single_marker_data.update({"type": marker_name})
                    markers.append(single_marker_data)

            elif isinstance(marker_data, dict):
                marker_data.update({"type": marker_name})
                markers.append(marker_data)
        markers = remove_overlap(markers, all_units)

    if markers == None or markers == []:
        markers = f_viewer_squares
    if markers == None or markers == []:
        markers = f_purple_squares
    if markers == None or markers == []:
        print(
            f"Account: {name}: Something went wrong while trying to find an area to place at {cap_nm}."
        )

    markers = shuffle_markers(markers, cap_coors, all_units)

    return markers[:100]


# Get markers that are closest to an unit of interest or shuffle everything.
def shuffle_markers(markers, cap_coors, all_units):
    # Shuffle or get coordinates of interest.
    if cap_coors == {} and all_units == []:
        return random.shuffle(markers)
    if len(cap_coors) == 0:
        f_l = [item for item in all_units if item["userId"] != ""]
        ref_unit = random.choice(f_l)
    else:
        ref_unit = cap_coors

    # Sort markers based on how close they are to the reference unit
    def euclidean_distance(p1, p2):
        x1, y1 = float(p1["x"]), float(p1["y"])
        x2, y2 = float(p2["x"]), float(p2["y"])

        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    for marker in markers:
        marker["distance_to_ref"] = euclidean_distance(marker, ref_unit)

    sorted_markers = sorted(markers, key=lambda x: x["distance_to_ref"])
    for marker in sorted_markers:
        del marker["distance_to_ref"]

    return sorted_markers


# Remove occupied markers since they can't be used
def remove_overlap(squares_of_interest, overlapping_squares):
    if not squares_of_interest:
        return []

    # Filter squares_of_interest to remove duplicates based on x and y
    unique_squares = []
    seen_coords = set()

    unique_squares = []
    seen_coords = set()

    for square in squares_of_interest:
        coord = (square["x"], square["y"])
        if coord not in seen_coords:
            seen_coords.add(coord)
            unique_squares.append(square)
    if unique_squares == None:
        return []
    # Filter out overlapping squares

    def squares_overlap(square1, square2):
        x1, y1, w1, h1 = map(
            float, [square1["x"], square1["y"], square1["width"], square1["height"]]
        )
        # TODO REVIEW TO MAKE SURE EPIC UNITS ARE GETTING THE CORRECT VALUE AS THEY MIGHT BE CAUSING THE OVER_UNIT ERROR
        x2, y2, w2, h2 = map(
            float,
            [
                square2["x"],
                square2["y"],
                square2.get("width", 0.8),
                square2.get("height", 0.8),
            ],
        )

        x_overlap = (x1 < x2 + w2) and (x2 < x1 + w1)
        y_overlap = (y1 < y2 + h2) and (y2 < y1 + h1)
        return x_overlap and y_overlap

    return [
        square
        for square in unique_squares
        if not any(squares_overlap(square, o) for o in overlapping_squares)
    ]


# Create imaginary markers since there aren't any on the map.
def make_imaginary_mkrs(zones):
    if zones == []:
        return []
    markers = []
    for zone in zones:
        x = zone["x"]
        y = zone["y"]
        width = zone["width"]
        height = zone["height"]

        num_markers_x = int(width / 0.8)
        num_markers_y = int(height / 0.8)

        for i in range(num_markers_x):
            for j in range(num_markers_y):
                # x, y = format_coors(x, y)
                marker = {
                    "x": round(round(x + i * 0.8, 2) + 0.4, 2),
                    "y": round(round(y + j * 0.8, 2) + 0.4, 2),
                    "width": 0.8,
                    "height": 0.8,
                    "type": "Vibe",
                }
                markers.append(marker)

    return markers


# The markers have a coordinate system of top and left. Convert to cartesian system with 0,0 at the center
def process_markers(raidPlan, map_width, map_height):
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
                "y": (float(map_height) / 2.0 - (float(values[i + 1]))) * 0.8,
                "width": base_dimensions,
                "height": base_dimensions,
            }

            temp_list.append(entry)

        # Store the list of entries for each key in the dictionary
        dict_of_markers[key] = temp_list

    return dict_of_markers
