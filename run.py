import asyncio, sys
import threading
from utils.settings import (
    write_file,
    open_file,
    setup_accounts,
    clean_temp_times,
    remove_duplicate_ids,
)
from utils.game_requests import set_user_data, check_for_new_event, update_unit_cooldown
from utils.behavior_emulator import start_up_requests, make_dummy_requests
from utils.player import fill_slots
from utils.place_units import place_unit_in_battlefield
from utils import constants
from utils.create_accounts import create_account


# Error interceptor
def custom_exception_handler(exc_type, exc_value, exc_traceback):
    print(
        f"Intercepted error: {exc_type.__name__}: {exc_value}\nTraceback: {exc_traceback}"
    )


async def run():
    
    # Cheap error handling
    sys.excepthook = custom_exception_handler
    
    # Check if accounts file exist, if not create one.
    data = open_file(constants.py_accounts)
    if data is None:
        create_account()
        return

    print(constants.welcome_banner)

    print("Starting up...")
    # Add user-agents, proxies and remove duplicates entries
    data = setup_accounts(data)

    print("Checking configuration file...")
    # Load unitIds and units.
    data = set_user_data(data)

    # Remove old temporary captain data
    print("Removing old temporary times...")
    data = clean_temp_times(data)

    # Remove duplicate userIds
    print("Removing duplicate accounts...")
    data = remove_duplicate_ids(data)

    # Write changes to storage
    write_file(constants.py_accounts, data)
    print("Saved changes.")

    print("Checking current event...")
    # Check if there's a new event and get new map nodes
    check_for_new_event()

    print("Running start up tasks once...")
    # Start up dummy requests here
    asyncio.create_task(start_up_requests())

    # Periodic requests here
    asyncio.create_task(make_dummy_requests())
    print("Periodic tasks have started.")

    # Fill and clean slots
    asyncio.create_task(fill_slots())
    print("Slot manager has started.")

    update_unit_cooldown()
    print("Units cooldown updated.")

    # Place units on the battlefield
    asyncio_thread = threading.Thread(
        target=lambda: asyncio.run(place_unit_in_battlefield())
    )
    asyncio_thread.start()
    print("Unit placement manager has started.")

    print("All start up tasks performed!")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(run())
