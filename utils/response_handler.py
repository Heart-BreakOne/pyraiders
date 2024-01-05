
#There was an error, wait and break
import inspect
import time

from utils.game_requests import check_for_new_event

# Check if server responded with an error.
def handle_error_response(response):
   
    response = response.json()
    
    if response["status"] == "error":
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name if caller_frame else "Unknown"
        
        if caller_name == "get_game_data":
            return False
        
        print("An error occurred while performing request.")
        if response["errorMessage"] == "Client lower." or response["errorMessage"] == "Game data mismatch.":
            print("Game version changed, you may need to restart the tool. Will try to hot update the event data.")
            check_for_new_event()
            time.sleep(60)
            return True
        else:
            print("Server responded with an error. Will wait 60 seconds before trying again.")
            time.sleep(60)
            return True
    else:
        return False