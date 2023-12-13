import asyncio
from utils.settings import write_file, open_file, setup_accounts, clean_temp_times
from utils.game_requests import set_user_data, check_for_new_event
from utils.behavior_emulator import start_up_requests, make_dummy_requests
from utils.player import fill_slots
from utils import constants
from utils.create_accounts import create_account


async def main():
    # Check if accounts file exist, if not create one.
    data = open_file(constants.py_accounts)
    if data is None:
        create_account()
        return
    
    
    # Add user-agents, proxies and remove duplicates entries
    data = setup_accounts(data)

    # Load unitIds and units.
    data = set_user_data(data)
    
    #Remove old temporary captain data
    data = clean_temp_times(data)
    
    #Write changes to storage
    write_file(constants.py_accounts, data)
    
    #Check if there's a new event and get new map nodes
    check_for_new_event()
    
    # Start up dummy requests here
    asyncio.create_task(start_up_requests())

    # Periodic requests here
    asyncio.create_task(make_dummy_requests())
    
    #Fill and clean slots
    asyncio.create_task(fill_slots())
    

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
