import asyncio
import time
from datetime import datetime
from utils import constants
from utils.settings import open_file
from utils.player import getActiveraids
from utils.time_generator import placement_minimum


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
            await asyncio.get_event_loop().run_in_executor(None, time.sleep, 5)
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

        # Check if raid response was properly received
        if raids == None:
            continue
        """
        for raid in raids:
            
            # Check if raid is over to collect rewards
            
            
            # Check if there are any raids in active placement as everything from this point on would be a waste of resources.
            
            
            #check if account is on active mode
            "powered_on": true,
            
            
            # Check if raid captain is on blocklist and skip (Redudancy check since the slot script is supposed to skip blocklisted captains)
            
            
            # Check loyalty preservation
            "preserve_loyalty": 0,
            "switch_if_preserve_loyalty": false,
            
            # Check raid type, check if an unit was placed, check if the user wants more units.
            "unlimited_campaign": false,
            "unlimited_clash": false,
            "unlimited_duels": false,
            "unlimited_dungeons": false,
            
            # Check if it is time and if there is time to place an unit
            
            
            # update units cooldown
            
            
            #cry and calculate placement using magic
            
            
            #get available unit that is highest on the list
            
            
            #Place the unit
            #print(raid)
            pass
        """
