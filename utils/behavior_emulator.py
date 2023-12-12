# This file handles requests that a legitimate browser session makes from time to time.

import asyncio, requests
from utils.time_generator import get_twenty
from utils import constants
from utils.settings import open_file
from utils.game_requests import get_request_strings, get_game_data, get_proxy_auth

#Requester
async def requester(user_id, token, user_agent, proxy, _, __, list_of_urls, proxy_user, proxy_pass):
    headers, proxies = get_request_strings(token, user_agent, proxy)
    has_proxy, proxy_auth = get_proxy_auth(proxy_user, proxy_pass)
    
    for url in list_of_urls:
        await asyncio.sleep(0.1)
        if has_proxy:
            requests.get(url, proxies=proxies, headers=headers, auth=proxy_auth)
        else:
            requests.get(url, proxies=proxies, headers=headers)  
        #If needed, print the response to check the content
        #response = print(response.json())
        #print(f"Random request successful for account {user_id}")
        
        
#These are the requests made periodically by the game
async def make_dummy_requests():

    #Sleep before repeating
    while True:
        await asyncio.sleep(get_twenty())
        accounts = open_file(constants.py_accounts)
    
        accounts = open_file(constants.py_accounts)
        

        tasks = []
        for account in accounts:
            if account["powered_on"] == False:
                continue
            user_id = account["userId"]
            token = account["token"]
            user_agent = account["user_agent"]
            proxy = account["proxy"]
            proxy_user = account["proxy_user"]
            proxy_password = account["proxy_password"]
            
            version, data_version = get_game_data(token, user_agent, proxy, proxy_user, proxy_password)
            list_of_periodic_requests = [
                f"{constants.gameDataURL}?cn=getLiveAndPlayingCaptainCount&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getLiveAndPlayingCaptainCount&clientVersion={version}&clientPlatform=WebGL",
                f"{constants.gameDataURL}?cn=getActiveRaidsByUser&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getActiveRaidsByUser",
                f"{constants.gameDataURL}?cn=getUser&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getUser&clientVersion={version}&clientPlatform=WebGL",
                f"{constants.gameDataURL}?cn=getFactionInfo&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getFactionInfo&clientVersion={version}&clientPlatform=WebGL",
                f"{constants.gameDataURL}?cn=getOpenCountTrackedChests&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getOpenCountTrackedChests&clientVersion={version}&clientPlatform=WebGL",
                f"{constants.gameDataURL}?cn=getCurrentStoreItems&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getCurrentStoreItems&clientVersion={version}&clientPlatform=WebGL",
                f"{constants.gameDataURL}?cn=getAvailableCurrencies&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getAvailableCurrencies&clientVersion={version}&clientPlatform=WebGL",
            ]
            task = requester(user_id, token, user_agent, proxy, version, data_version, list_of_periodic_requests, proxy_user, proxy_password)
            tasks.append(task)

        await asyncio.gather(*tasks)




#These are the requests made when the game starts up      
async def start_up_requests():
    accounts = open_file(constants.py_accounts)

    tasks = []
    for account in accounts:
        if account["powered_on"] == False:
            continue
        user_id = account["userId"]
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        proxy_user = account["proxy_user"]
        proxy_password = account["proxy_password"]
        version, data_version = get_game_data(token, user_agent, proxy, proxy_user, proxy_password)
        
        list_of_dummy_requests = [
            f"{constants.gameDataURL}?cn=trackEvent&command=trackEvent&eventName=load_timing_init&eventData=%7B%22Type%22%3A%22Init%22%7D",
            f"{constants.gameDataURL}?cn=getLocalization&gameDataVersion={data_version}&command=getLocalization&language=en-us&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getPurchaseResults&gameDataVersion={data_version}&command=getPurchaseResults&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getCurrentTime&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getCurrentTime&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getUserUnits&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getUserUnits&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getUserSouls&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getUserSouls&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getCurrentStoreItems&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getCurrentStoreItems&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getUserEventProgression&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getUserEventProgression&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getActiveAmbassadors&userId={user_id}&isCaptain=0&gameDataVersion=9f44db04a",
            f"{constants.gameDataURL}?cn=getUserItems&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getUserItems&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getUserQuests&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getUserQuests&clientVersion={version}&clientPlatform=WebGL",
            f"{constants.gameDataURL}?cn=getAvailableCurrencies&userId={user_id}&isCaptain=0&gameDataVersion={data_version}&command=getAvailableCurrencies&clientVersion={version}&clientPlatform=WebGL",
        ]

        task = requester(user_id, token, user_agent, proxy, version, data_version, list_of_dummy_requests, proxy_user, proxy_password)
        tasks.append(task)

    await asyncio.gather(*tasks)