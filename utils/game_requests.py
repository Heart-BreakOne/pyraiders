import json, requests
from utils.settings import open_file

def get_variables():
    settings_data = open_file()
    version = settings_data.get('version', {})
    data_version =  settings_data.get('data_version', {})
    userId =  settings_data.get('userId', {})
    access_info = settings_data.get('access_info', {})
    user_agent = settings_data.get('user_agent', {})
    headers = {
        'Cookie': "ACCESS_INFO=" + access_info,
        'User-Agent': user_agent
    }
    return {'version': version, 'data_version': data_version, 'userId': userId, 'headers': headers}


def get_display_data():
    variables = get_variables()
    url = "https://www.streamraiders.com/api/game/?cn=getAvailableCurrencies&userId=" + str(variables['userId']) + "&isCaptain=1&gameDataVersion="+ str(variables['data_version']) +"&command=getAvailableCurrencies&clientVersion="+ str(variables['version']) +"&clientPlatform=WebGL"
    response = requests.get(url, headers=variables['headers'])
    if response.status_code == 200:
        return response.json()
    
def get_units_data():
    with open('.pyraiders_settings.json', 'r') as file:
        settings = json.load(file)

    if 'userUnits' not in settings:
        variables = get_variables()
        url = "https://www.streamraiders.com/api/game/?cn=getUserUnits&userId=" + str(variables['userId']) + "&isCaptain=1&gameDataVersion="+ str(variables['data_version']) +"&command=getUserUnits&clientVersion="+ str(variables['version']) +"&clientPlatform=WebGL"
        response = requests.get(url, headers=variables['headers'])
        if response.status_code == 200:
            units = response.json().get("data", [])
            for each_unit in units:
                each_unit['priority'] = 0
            #add an integer key called priority to each item before saving
            settings['userUnits'] = units
            with open('.pyraiders_settings.json', 'w') as file:
                json.dump(settings, file, indent=2)