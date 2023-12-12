import asyncio
from utils.settings import write_file, open_file, setup_accounts
from utils.game_requests import set_user_data
from utils.behavior_emulator import start_up_requests, make_dummy_requests
from utils.player import play
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

    write_file(constants.py_accounts, data)
    
    # Start up dummy requests here
    asyncio.create_task(start_up_requests())

    # Periodic requests here
    asyncio.create_task(make_dummy_requests())
    
    #Play the game
    asyncio.create_task(play())

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
