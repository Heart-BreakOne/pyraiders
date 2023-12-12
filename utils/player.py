import asyncio
from utils.time_generator import get_four_quarters
from utils.settings import open_file


async def play():
    while True:
        await asyncio.sleep(get_four_quarters())
        print("We are playing!")

        # Two tasks to conduct in here

        # Fill empty slots.

        # Place units.


def fill_slots():
    # TODO fill slots
    pass


def place_units():
    # TODO place units
    pass
