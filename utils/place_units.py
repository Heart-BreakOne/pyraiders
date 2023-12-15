import asyncio
import threading
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
            groups = [
                accounts[i : i + group_size]
                for i in range(0, len(accounts), group_size)
            ]

            await process_groups(groups)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await asyncio.get_event_loop().run_in_executor(None, time.sleep, 10)
            print(datetime.now())
            is_running = False
            print("Placed all possible units")


# Split the groups into tasks so they can be run simultaneously
async def process_groups(groups):
    tasks = []

    for group in groups:
        task = asyncio.create_task(process_group(group))
        tasks.append(task)
    await asyncio.gather(*tasks)


# Process the accounts in groups. The task handler ensure they run simultaneously
async def process_group(group):
    print(f"Processing group")

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
        for raid in raids:
            print(raid)
