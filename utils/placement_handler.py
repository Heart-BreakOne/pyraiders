import requests
from shapely.geometry import box, Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from shapely.geometry.collection import GeometryCollection
from utils import constants
from utils.game_requests import get_proxy_auth, get_request_strings


def calculate_placement(
    raid,
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
    # Draw imaginary map
    # Map tiles
    viewer_zones = MapData["PlayerPlacementRects"]
    purple_zones = MapData["HoldingZoneRects"]
    ally_zones = MapData["AllyPlacementRects"]
    enemy_zones = MapData["EnemyPlacementRects"]
    neutral_zones = MapData["NeutralPlacementRects"]

    intersecting_zones = ally_zones + enemy_zones + neutral_zones

    f_viewer_zones = filter_zones(viewer_zones, intersecting_zones)
    f_purple_zones = filter_zones(purple_zones, intersecting_zones)

    rf_viewer_zones = filter_zones(viewer_zones, purple_zones) or (
        f_viewer_zones + f_purple_zones
    )
    #Output the map for testing
    #output_plot(rf_viewer_zones)
    
    
    #Units, allies, neutrals and obstacles across the map
    units_coors = MapData["PlacementData"]
    obstacles_coors = MapData["ObstaclePlacementData"]

    pass


def split_zone(zone, intersecting_zones):

    
    zone_polygon = box(
        float(zone["x"]), float(zone["y"]), float(zone["x"]) + float(zone["width"]), float(zone["y"]) + float(zone["height"])
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

#Generate a png with the map plot
def output_plot(rf_viewer_zones):
    # Create a plot
    fig, ax = plt.subplots()

    # Plot each polygon
    for zones in rf_viewer_zones:
        x, y = zones.exterior.xy
        ax.fill(x, y, alpha=0.5)

    # Set axis labels
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Save the plot to a file instead of showing it
    plt.savefig('output_plot.png')
    plt.close()