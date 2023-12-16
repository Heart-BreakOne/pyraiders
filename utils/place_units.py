import asyncio
import time
from datetime import datetime, timedelta
from utils import constants
from utils.game_requests import collect_raid_rewards, get_game_data, leave_captain, update_unit_cooldown
from utils.placement_handler import calculate_placement
from utils.settings import open_file
from utils.player import getActiveraids


async def place_unit_in_battlefield():
    is_running = False

    while True:
        if is_running:
            print("We are running already")
            return
        is_running = True

        try:
            # Divide the account into 4 groups for simultaneous processing
            accounts = open_file(constants.py_accounts)
            accs_quantity = len(accounts)
            if accs_quantity == 0:
                return
            group_size = len(accounts) // 4
            if group_size == 0:
                group_size = 1
            groups = [
                accounts[i : i + group_size]
                for i in range(0, len(accounts), group_size)
            ]

            await process_groups(groups)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await asyncio.get_event_loop().run_in_executor(None, time.sleep, 3)
            is_running = False
            print("Placed all possible units")
            print(datetime.now())


# Split the groups into tasks so they can be run simultaneously
async def process_groups(groups):
    tasks = []

    for group in groups:
        task = asyncio.create_task(process_group(group))
        tasks.append(task)
    await asyncio.gather(*tasks)


# Process the accounts in groups. The task handler ensure they run simultaneously
async def process_group(group):
    
    for account in group:
        #Check if account is enabled
        if not account["powered_on"]:
            continue
        name = account["name"]    
        user_id = account["userId"]
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        proxy_user = account["proxy_user"]
        proxy_password = account["proxy_password"]
        # Get active raids to determine placements
        raids = getActiveraids(
            user_id, token, user_agent, proxy, proxy_user, proxy_password
        )
        version, data_version = get_game_data(
            token, user_agent, proxy, proxy_user, proxy_password
        )

        # Check if raid response was properly received
        if raids == None:
            continue

        for raid in raids:
            raid_id = raid["raidId"]
            cap_nm = raid["twitchUserName"]
            cap_id = raid["captainId"]
            # Check if raid is over to collect rewards #also check rewards was not collected already
            if raid["hasRecievedRewards"] == "0" and raid["postBattleComplete"] == "1" and raid["hasViewedResults"] == "0":
                # Raid is complete, collect rewards and return so the battle is checked on the next loop
                collect_raid_rewards(name, cap_nm, user_id, raid_id, token, user_agent, proxy, proxy_user, proxy_password, version, data_version)
                continue

            # Check if raid is in active placement as everything from this point on would be a waste of resources.
            now = datetime.utcnow()
            cr_time_string = raid["creationDate"]
            creation_time = datetime.strptime(cr_time_string, "%Y-%m-%d %H:%M:%S")
            time_difference = now - creation_time

            raid_type = raid["type"]
            if raid_type == "1":
                # Campaign
                if time_difference > timedelta(minutes=29, seconds=50):
                    continue
            elif raid_type == "2" or raid_type == "5":
                # Duels and clash
                if time_difference > timedelta(minutes=6, seconds=55):
                    continue
            elif raid_type == "3":
                # Dungeons
                if time_difference > timedelta(minutes=5, seconds=55):
                    continue


            # Check if raid captain is on blocklist and skip (Redudancy check since the slot script is supposed to skip blocklisted captains)
            blocklist = account["blocklist"]
            if raid["twitchUserName"].upper() in map(str.upper, blocklist):
                continue
            
            #Check if it's campaign and if user wants to preserver loyalty.
            if account["preserve_loyalty"] != 0 and raid_type == "1":
                mapLoyalty = raid["pveLoyaltyLevel"]
                loyal = account["preserve_loyalty"]
                #Check if map loyalty is bigger than the.
                if loyal < mapLoyalty:
                    current_map_node = raid["nodeId"]
                    map_nodes = open_file("assets/map_nodes")
                    # Check the loyalty on the current based on the map id.
                    if current_map_node in map_nodes:
                        chest_type = map_nodes[current_map_node]["ChestType"]
                        chests = constants.regular_chests
                        if chest_type not in chests:
                            if account["switch_if_preserve_loyalty"]:
                                leave_captain(cap_id, cap_nm, user_id, token, user_agent, proxy, proxy_user, proxy_password)
                                continue
                            else:
                                continue
            
            # Check if it is time and if there is time to place an unit
            now = datetime.utcnow()
            last = raid["lastUnitPlacedTime"]
            previous_placement = (
                datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                if raid["lastUnitPlacedTime"]
                else None
                )
            
            if raid_type == "1":
                # Campaign
                time_since_creation = now - creation_time if creation_time else timedelta(0)
                time_since_previous_placement = now - previous_placement if previous_placement else timedelta(minutes=6)
                if (
                    time_since_creation <= timedelta(minutes=1, seconds=30) or
                    time_since_creation > timedelta(minutes=29, seconds=55) or
                    time_since_previous_placement < timedelta(minutes=5)
                ):
                    continue
            elif raid_type == "2" or raid_type == "5":
                time_since_creation = now - creation_time if creation_time else timedelta(0)
                time_since_previous_placement = now - previous_placement if previous_placement else timedelta(minutes=2)
                if (
                    time_since_creation <= timedelta(minutes=1, seconds=5) or
                    time_since_creation > timedelta(minutes=6, seconds=55) or
                    time_since_previous_placement < timedelta(minutes=2, seconds=00)
                ):
                    continue
            elif raid_type == "3":
                # Dungeons
                time_since_creation = now - creation_time if creation_time else timedelta(0)
                time_since_previous_placement = now - previous_placement if previous_placement else timedelta(minutes=2)
                if (
                    time_since_creation <= timedelta(minutes=1, seconds=5) or
                    time_since_creation > timedelta(minutes=5, seconds=55) or
                    time_since_previous_placement < timedelta(minutes=1, seconds=40)
                ):
                    continue
            
            
            # Check raid type, check if an unit was placed, check if the user wants more units.
            un_key = constants.type_dict.get(raid_type)
            if last is not None and un_key is not None and account[un_key]:
                continue
            
            # update units cooldown
            update_unit_cooldown()
            
            #cry and calculate placement using magic
            url = constants.mapPlacements + raid["battleground"] + ".txt"
            calculate_placement(url)
            
            #get available unit that is highest on the list
            
            
            #Place the unit
            #print(raid)
            pass
