import asyncio
from utils.time_generator import get_four_quarters
from utils.settings import open_file
from utils import constants


async def play():
    while True:
        await asyncio.sleep(get_four_quarters())
        print("We are playing!")

        # Two tasks to conduct in here

        # Fill empty slots.

        # Place units.
        
def fill_slots():
    
    accounts = open_file(constants.py_accounts)
    for account in accounts:
        #Check if account is running
        if account["powered_on"] == False:
            continue
        #Required data
        userId = account["userId"]
        token = account["token"]
        user_agent = account["user_agent"]
        proxy = account["proxy"]
        
        #Data for the conditional checks
        preserve_loyalty = account["preserve_loyalty"]
        switch_if_no_loyalty = account["switch_if_no_loyalty"]
        switch_on_idle = account["switch_on_idle"]
        if switch_on_idle:
            minimum_idle_time = account["minimum_idle_time"]
        unlimited_campaign = account["unlimited_campaign"]
        unlimited_pvp = account["unlimited_pvp"]
        only_masterlist = account["only_masterlist"]
        if only_masterlist:
            masterlist = account["masterlist"]
        ignore_blacklist = account["ignore_blacklist"]
        if blacklist:
            blacklist = account["blacklist"]
        favorites_only = account["favorites_only"]
        if favorites_only:
            favoriteCaptainIds = account["favoriteCaptainIds"]
        any_captain = account["any_captain"]
        temporary_ignore = account["temporary_ignore"]
        
        
    # Task 2 -> Check how many slots are occupied and if the user has battlepass to determine how many slots are available for placement.
    # Task 3 -> Place available greenlighted captains based on the ruleset on any slots that may be available.
    # Task 4 -> Flag captains that may be idling.
    # Task 5 -> Check if there greenlighted captains and if there idling captains. Replace them.
    
    # TODO fill slots
    pass


def place_units():
    # TODO place units
    pass
