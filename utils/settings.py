import json
import random
import os
import requests
from utils import constants

#Get current game version and dataVersion. Validate user token, if not correct, return false
def get_user():
    gameDataResponse = requests.get(constants.gameDataURL)
    # Check if the request was successful (status code 200)
    if gameDataResponse.status_code == 200:
        # Print the response content
        response_json = gameDataResponse.json()

        # Extract version from the JSON response
        version = response_json['info']['version']
        data_version = response_json['info']['dataVersion']
        validateURL = "https://www.streamraiders.com/api/game/?cn=getUser&gameDataVersion="+ data_version +"0&command=getUser&skipDataCheck=true&isLogin=true&clientVersion="+ version + "&clientPlatform=WebGL"
        
        settings_data = open_file(constants.py_captain)
        access_info = settings_data.get('access_info', {})
        user_agent = settings_data.get('user_agent', {})
        headers = {
            'Cookie': "ACCESS_INFO=" + access_info,
            'User-Agent': user_agent
        }
            
        response = requests.get(validateURL, headers=headers)
        if response.status_code == 200:
            currentResponse = response.json()
            isCaptain = currentResponse["data"]["isCaptain"]
            if (isCaptain != '1'):
                return False
            else:
                userId = currentResponse["data"]["userId"]
                captainUserName = currentResponse["data"]["twitchUserName"]
                data_to_save = {'userId': userId, 'captainUserName': captainUserName, 'version': version, 'data_version': data_version}
                
                existing_data = {}
                
                existing_data = open_file(constants.py_captain)
                existing_data.update(data_to_save)
                write_file(constants.py_captain, existing_data)
                return True
        else:
            return False 
    else:
        # Print an error message if the request was not successful
        return False
    
def check_settings():
    file_path = constants.py_captain
    if os.path.exists(file_path):
        return True
    else:
        return False

def save_settings(ACCESS_INFO):   
    random_user_agent = random.choice(constants.user_agents)
    
    # Save the data to a JSON file
    data_to_save = {'access_info': ACCESS_INFO, 'user_agent': random_user_agent}
    write_file(constants.py_captain, data_to_save)
        
def delete_settings():
    os.remove(constants.py_captain)
    
def open_file(file_name):
     with open(file_name, "r") as json_file:
        settings_data = json.load(json_file)
        return settings_data
    
def write_file(file_name, data_to_save):
     with open(file_name, "w") as json_file:
        json.dump(data_to_save, json_file, indent=2)