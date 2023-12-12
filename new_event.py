import requests
from utils import current_event
from utils.settings import write_file
# When an new event starts, run:    python3 new_event.py

"""WHEN A NEW EVENT STARTS, TWO THINGS CHANGE:
THE EVENT ID.
THE MAP IDS.

I haven't figured it out a smart out to obtain the current event id with precision, so an update on the event Id is required whenever a new event starts.

The other data that changes are the map Ids, those ids are contained in a very large file (~40MB, with 1.8kk lines).
It's possible to fetch the file and extract the mapIds everytime the tool is started up,
but considering the size of the file and the fact that the data of interest only changes when an event starts I don't believe it's a resonable action to do.

For this reason I included this helper to update the event Id and the new maps Id.
Simply run:    python3 new_event.py

P.S. Even when the event is a rerun, the map Ids change as well.
The event ID needs to be manually changed so it may take up to a day for me to do it, you can do it yourself by accessing: 
https://www.streamraiders.com/api/game/?cn=getEventProgressionLite<userId>&isCaptain=0&gameDataVersion=<dataVersion>&command=getUserEventProgression&clientVersion=<version>&clientPlatform=WebGL
It wil give an error saying the client is lower. Change <dataVersion> and <version> with the values on the screen. Change the <userId> with any one value in the py_accounts.json.
Refresh the page and properly locate the current event id.
Go to /utils/current_event.py and replace the string that is there and you are set.

The mapIds are managed automatically by this helper.
"""

keys_to_remove = ['NodeDifficulty', 'MapTags', 'OnLoseDialog', 'OnStartDialog', 'OnWinDialog']

def main():
    
    #Update event ID first
    response = requests.get("https://heart-breakone.github.io/webpages/current_event_id.json")
    if response.status_code == 200:
        fetch_event = response.json()
        fetch_event = fetch_event["current_event"]
        if fetch_event == current_event.current_event:
            print("The are no event IDs to update. Current event ID is " + fetch_event + ".\nIf a new event has started you may update it manually.")
        else:
            print("Event ID updated")
            with open("utils/current_event.py", "w") as file:
                file.write('current_event = "'+ fetch_event + '"')
    else:
        print(f"Error: {response.status_code}")


    #Update mapIds 
    print("\n\nNow getting map nodes, this may take a few seconds...")
    response = requests.get("https://streamcap-prod1.s3.amazonaws.com/data/data.9f44db04a984.json")
    if response.status_code == 200:
        data_json = response.json()
        data_json = data_json["sheets"]
        data_json = data_json["MapNodes"]
        for entry in data_json.values():
            for key in keys_to_remove:
                entry.pop(key, None)
        write_file("assets/map_nodes.json", data_json)        
        print("Map nodes updated successfully.")
    else:
        print(f"Error: {response.status_code}")
    
if __name__ == "__main__":
    main()
