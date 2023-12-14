import asyncio
import concurrent.futures
from utils import constants
from utils.player import getActiveraids
from utils.settings import open_file
from utils.time_generator import placement_minimum


async def place_unit_in_battlefield():
    is_running = False
    lock = asyncio.Lock()

    while True:
        await asyncio.sleep(placement_minimum())
        async with lock:
            if is_running:
                print("We are running already")
                return
            is_running = True

        try:
            accounts = open_file(constants.py_accounts)

            accs_quantity = len(accounts)
            if accs_quantity == 0:
                return

            group_size = max(accs_quantity // 4, 1)
            total_groups = (accs_quantity + group_size - 1) // group_size

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = []

                for group_number in range(total_groups):
                    start_index = group_number * group_size
                    end_index = (group_number + 1) * group_size
                    group_accounts = accounts[start_index:end_index]

                    future = asyncio.to_thread(process_group_sync, group_accounts)
                    futures.append(future)

                await asyncio.gather(*futures)

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            async with lock:
                is_running = False


def process_group_sync(group_accounts):
    asyncio.run(process_group(group_accounts))
   
async def process_group(group_accounts):
    #Determine whether or not units will be placed
    print("Placing units at random point between 5 and 15 seconds.")
    return
    for account in group_accounts:
        user_id = account["userId"]
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        proxy_user = account["proxy_user"]
        proxy_password = account["proxy_password"]
        #Get active raids to determine placements
        raids = getActiveraids(user_id, token, user_agent, proxy, proxy_user, proxy_password)
        for raid in raids:
            print(raid)
        
        
