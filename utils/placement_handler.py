import requests

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import box, Polygon
from shapely.geometry.collection import GeometryCollection

from utils import constants
from utils.settings import open_file
from utils.game_requests import get_proxy_auth, get_request_strings


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

    # Using the raid, raid plan and map calculate placement
    # print(getRaid)
    # print("\n")
    # print(raidPlan)
    # print("\n")

    ## Logic based on projectbots
    # Have no clue how to get the dimensions of some of the sprites.
    # obstacles_coors = MapData["ObstaclePlacementData"]

    # Units, allies, neutrals across the map
    h_units = getRaid["data"]["placements"]
    ai_units = MapData["PlacementData"]
    all_units = h_units + ai_units
    map_units = open_file(constants.map_units_path)
    cap_coors = []
    
    for unit in all_units:
        
        unit_name = unit["CharacterType"]
    
        for key, units in map_units.items():
            if key == unit_name:
                is_epic = units["IsEpic"]
                cube_dimension = units["Size"]
                unit["IsEpic"] = is_epic
                if is_epic:
                    cube_dimension = cube_dimension * 2
                    
                unit["width"] = cube_dimension
                unit["height"] = cube_dimension
                if unit["userId"] == cap_id:
                    cap_coors = [unit["X"], unit["Y"]]
                break
            # Modify keys in ai_unit
        unit["x"] = unit.pop("X")
        unit["y"] = unit.pop("Y")
                    
    # Draw imaginary map
    # Map tiles
    
    viewer_zones = MapData["PlayerPlacementRects"]
    purple_zones = MapData["HoldingZoneRects"]
    ally_zones = MapData["AllyPlacementRects"]
    enemy_zones = MapData["EnemyPlacementRects"]
    neutral_zones = MapData["NeutralPlacementRects"]
    
    pass


def split_zone(zone, intersecting_zones):
    zone_polygon = box(
        float(zone["x"]),
        float(zone["y"]),
        float(zone["x"]) + float(zone["width"]),
        float(zone["y"]) + float(zone["height"]),
    )

    for intersecting_zone in intersecting_zones:
        intersecting_polygon = box(
            float(intersecting_zone["x"]),
            float(intersecting_zone["y"]),
            float(intersecting_zone["x"]) + float(intersecting_zone["width"]),
            float(intersecting_zone["y"]) + float(intersecting_zone["height"]),
        )

        zone_polygon = zone_polygon.difference(intersecting_polygon)
    if zone_polygon.is_empty:
        return []
    else:
        return [box(*zone_polygon.bounds)]


def filter_zones(viewer_zones, intersecting_zones):
    return [
        part
        for viewer_zone in viewer_zones
        for part in split_zone(viewer_zone, intersecting_zones)
    ]

























# Output the map picture for testing
#output_plot(cap_nm, rf_viewer_zones)
# Generate a png with the map plot
def output_plot(cap_nm, rf_viewer_zones):
    # Create a plot
    fig, ax = plt.subplots()

    # Plot each polygon
    for zones in rf_viewer_zones:
        x, y = zones.exterior.xy
        ax.fill(x, y, alpha=0.5)

    # Set axis labels
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Save the plot to a file instead of showing it
    plt.savefig(f"{cap_nm}_output_plot.png")
    plt.close()
