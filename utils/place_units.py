import asyncio
import time
from datetime import datetime, timedelta
from utils import constants
from utils.game_requests import (
    collect_raid_rewards,
    get_game_data,
    leave_captain,
    update_unit_cooldown,
)
from utils.marker_handler import calculate_placement
from utils.placement_handler import place_the_unit
from utils.settings import check_raid_type, open_file, validate_raid
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
            print("Placement system cycled.")
            await asyncio.get_event_loop().run_in_executor(None, time.sleep, 20)
            is_running = False


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
        # Check if account is enabled
        if not account["powered_on"]:
            continue
        name = account["name"]
        user_id = account["userId"]
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        proxy_user = account["proxy_user"]
        proxy_password = account["proxy_password"]
        can_epic = account["use_potions"] 
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
            
            # Calculate the markers
            usable_markers = calculate_placement(
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
            )
            if usable_markers == []:
                return
            # Check if raid is over to collect rewards #also check rewards was not collected already
            if (
                raid["hasRecievedRewards"] == "0"
                and raid["postBattleComplete"] == "1"
                and raid["hasViewedResults"] == "0"
            ):
                # Raid is complete, collect rewards and return so the battle is checked on the next loop
                collect_raid_rewards(
                    name,
                    cap_nm,
                    user_id,
                    raid_id,
                    token,
                    user_agent,
                    proxy,
                    proxy_user,
                    proxy_password,
                    version,
                    data_version,
                )

            # Check if raid is in active placement as everything from this point on would be a waste of resources.
            now = datetime.utcnow()
            cr_time_string = raid["creationDate"]
            creation_time = datetime.strptime(cr_time_string, "%Y-%m-%d %H:%M:%S")
            time_difference = now - creation_time
            
            raid_type = raid["type"]
            
            if not check_raid_type(raid_type, time_difference):
                continue

            # Check if raid captain is on blocklist and skip (Redudancy check since the slot script is supposed to skip blocklisted captains)
            blocklist = account["blocklist"]
            if raid["twitchUserName"].upper() in map(str.upper, blocklist):
                continue

            # Check if it's campaign and if user wants to preserver loyalty.
            if account["preserve_loyalty"] != 0 and raid_type == "1":
                mapLoyalty = raid["pveLoyaltyLevel"]
                loyal = account["preserve_loyalty"]
                # Check if map loyalty is bigger than the.
                if loyal < mapLoyalty:
                    current_map_node = raid["nodeId"]
                    map_nodes = open_file("assets/map_nodes")
                    # Check the loyalty on the current based on the map id.
                    if current_map_node in map_nodes:
                        chest_type = map_nodes[current_map_node]["ChestType"]
                        chests = constants.regular_chests
                        if chest_type not in chests:
                            if account["switch_if_preserve_loyalty"]:
                                print("log 4")
                                leave_captain(
                                    cap_id,
                                    cap_nm,
                                    user_id,
                                    token,
                                    user_agent,
                                    proxy,
                                    proxy_user,
                                    proxy_password,
                                ) 
                                continue
                            else:
                                pass

            # Check if it is time and if there is time to place an unit
            last = raid["lastUnitPlacedTime"]
            previous_placement = (
                datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
                if raid["lastUnitPlacedTime"]
                else None
            )

            if not validate_raid(raid):
                continue

            # Check raid type, check if an unit was placed, check if the user wants more units.
            un_key = constants.type_dict.get(raid_type)
            if last is not None and un_key is not None and not account[un_key]:
                continue

            # update units cooldown
            update_unit_cooldown()
            time.sleep(2)
            # Check if there are units available in order to save resources
            units = check_unit_availability(name, now)
            if not units or units == []:
                continue


            #Place the unit
            place_the_unit(
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
                creation_time
            )



# Check if unit has priority and if it's out of cooldown.
def check_unit_availability(name, now):
    units = []
    accounts = open_file(constants.py_accounts)
    for account in accounts:
        if account["name"] == name:
            user_units = account["units"]
            break
    for unit in user_units:
        if unit["priority"] == 0:
            continue
        cooldown_str = unit["cooldownTime"]
        if cooldown_str == None:
            cooldown = now - timedelta(minutes=5)
        else:
            cooldown = datetime.strptime(cooldown_str, "%Y-%m-%d %H:%M:%S")
        if cooldown > now:
            continue
        else:
            units.append(unit)

    # Sort units based on their "priority" value in ascending order
    units.sort(key=lambda x: x["priority"])

    return units
