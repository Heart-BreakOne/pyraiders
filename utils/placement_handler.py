import requests
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
        + "&command=getRaid&raidId=" + raid_id + "&maybeSendNotifs=False&clientVersion="
        + version
        + "&clientPlatform=WebGL"
    )
    getRaidJson = None
    if has_proxy:
        getRaidJson = requests.get(gr_url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        getRaidJson = requests.get(gr_url, proxies=proxies, headers=headers)
    
    
     # Data on markers
    raidPlanJson = None
    r_url = ("https://www.streamraiders.com/api/game/?cn=getRaidPlan&userId=" + user_id + "&isCaptain=0&gameDataVersion=" + data_version + "&command=getRaidPlan&raidId=" + raid_id + "&clientVersion=" + version + "&clientPlatform=WebGL")
    if has_proxy:
        raidPlanJson = requests.get(r_url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        raidPlanJson = requests.get(r_url, proxies=proxies, headers=headers)
    
    # Data about the entire map.
    PlacementDataTxt = None
    pd_url = constants.mapPlacements + raid["battleground"] + ".txt"
    if has_proxy:
        PlacementDataTxt = requests.get(pd_url, proxies=proxies, headers=headers, auth=proxy_auth)
    else:
        PlacementDataTxt = requests.get(pd_url, proxies=proxies, headers=headers)
    getRaid = getRaidJson.json()
    raidPlan = raidPlanJson.json()
    PlacementData = PlacementDataTxt.json()
    
    if getRaid == None or raidPlan == None or PlacementData == None:
        print(f"Account {name}: something went wrong while trying to get placement data")
        return
    
    #Using the raid, raid plan and map calculate placement
    
    pass