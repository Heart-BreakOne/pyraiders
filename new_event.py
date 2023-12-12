import requests
from utils.settings import write_file
from utils import constants
# When an new event starts, run:    python3 new_event.py

"""When a new event starts, the map ids changes, even for reruns.

The map ids are contained in a large file (~40MB, with 1.8kk lines).
It's easily possible to fetch the file and extract the mapIds everytime the tool is started up,
but considering the size of the file and the fact that the data of interest only changes when a new event starts I don't believe it's a resonable action to do.

For this reason I included this helper to update the map IDs whenever a new event begins.
Simply run:    python3 new_event.py
"""

keys_to_remove = ['NodeDifficulty', 'MapTags', 'OnLoseDialog', 'OnStartDialog', 'OnWinDialog']

def main():
    
    #Update mapIds 
    print("Getting map nodes, this may take a few seconds...")
    response = requests.get(constants.map_nodes_url)
    if response.status_code == 200:
        data_json = response.json()["sheets"]["MapNodes"]
        for entry in data_json.values():
            for key in keys_to_remove:
                entry.pop(key, None)
        write_file(constants.map_nodes_path, data_json)        
        print("\nMap nodes updated successfully.\n")
    else:
        print(f"\nError: {response.status_code}")
    
if __name__ == "__main__":
    main()
