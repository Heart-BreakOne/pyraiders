import json
import random
import os
import requests

user_agents = [
    # Google Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    
    # Mozilla Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    
    # Apple Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
    
    # Microsoft Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.37",
]

gameDataURL = "https://www.streamraiders.com/api/game/"


#Get current game version and dataVersion. Validate user token, if not correct, return false
def get_user():
    gameDataResponse = requests.get(gameDataURL)
    # Check if the request was successful (status code 200)
    if gameDataResponse.status_code == 200:
        # Print the response content
        response_json = gameDataResponse.json()

        # Extract version from the JSON response
        version = response_json['info']['version']
        data_version = response_json['info']['dataVersion']
        validateURL = "https://www.streamraiders.com/api/game/?cn=getUser&gameDataVersion="+ data_version +"0&command=getUser&skipDataCheck=true&isLogin=true&clientVersion="+ version + "&clientPlatform=WebGL"
        with open('pycaptain_settings.json', 'r') as file:
            settings_data = json.load(file)
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
                
                with open("pycaptain_settings.json", "r") as json_file:
                    existing_data = json.load(json_file)
                existing_data.update(data_to_save)
               
                with open("pycaptain_settings.json", "w") as json_file:
                    json.dump(existing_data, json_file)
                return True
        else:
            return False 
    else:
        # Print an error message if the request was not successful
        return False
    

def check_settings():
    file_path = "pycaptain_settings.json"
    if os.path.exists(file_path):
        return True
    else:
        return False


        
def save_settings(ACCESS_INFO):   
    random_user_agent = random.choice(user_agents)
        

    # Save the data to a JSON file
    data_to_save = {'access_info': ACCESS_INFO, 'user_agent': random_user_agent}
    with open("pycaptain_settings.json", "w") as json_file:
        json.dump(data_to_save, json_file)
        

def delete_settings():
    os.remove("pycaptain_settings.json")
    
        
        