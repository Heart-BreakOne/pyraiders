import asyncio, sys
from utils.settings import write_file, open_file, setup_accounts, clean_temp_times, remove_duplicate_ids
from utils.game_requests import set_user_data, check_for_new_event, update_unit_cooldown
from utils.behavior_emulator import start_up_requests, make_dummy_requests
from utils.player import fill_slots
from utils.place_units import place_unit_in_battlefield
from utils import constants
from utils.create_accounts import create_account


def custom_exception_handler(exc_type, exc_value, exc_traceback):
    print(f"Intercepted error: {exc_type.__name__}: {exc_value}\nTraceback: {exc_traceback}")


async def run():
    # Cheap error handling
    sys.excepthook = custom_exception_handler
    # Check if accounts file exist, if not create one.
    data = open_file(constants.py_accounts)
    if data is None:
        create_account()
        return
    print("Starting up.")
    # Add user-agents, proxies and remove duplicates entries
    data = setup_accounts(data)
    
    print("Checking configuration file.")
    # Load unitIds and units.
    data = set_user_data(data)
    
    # Remove old temporary captain data
    data = clean_temp_times(data)

    # Remove duplicate userIds
    data = remove_duplicate_ids(data)
    
    # Write changes to storage
    write_file(constants.py_accounts, data)

    print("Checking current event.")
    # Check if there's a new event and get new map nodes
    check_for_new_event()

    print("Running start up tasks.")
    # Start up dummy requests here
    asyncio.create_task(start_up_requests())

    print("Periodic tasks have started.")
    # Periodic requests here
    asyncio.create_task(make_dummy_requests())

    print("Slot manager has started.")
    # Fill and clean slots
    asyncio.create_task(fill_slots())

    print("Unit placement manager has started.")
    # Place units on the battlefield
    asyncio.create_task(place_unit_in_battlefield())
    
    print("Unit cooldown management has started.")
    # Update unit cooldown time every 5 minutes
    asyncio.create_task(update_unit_cooldown())

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run())
