# This file handles requests that a legitimate browser session makes from time to time.

import asyncio
from utils.time_generator import get_twenty
async def make_dummy_requests():
    while True:
        print("hello")
        await asyncio.sleep(get_twenty())
        print("waited some random twenty")
