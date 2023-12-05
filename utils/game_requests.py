import json, requests

def get_variables():
    with open('pycaptain_settings.json', 'r') as file:
        settings_data = json.load(file)
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
        print(response.json())
        return response.json()
    
   
def get_units_data():
    with open('pycaptain_settings.json', 'r') as file:
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
            with open('pycaptain_settings.json', 'w') as file:
                json.dump(settings, file, indent=2)


















"""
auth_token = '733676827%3A6fd096cc2002bbc73b8e2c9a815c75cf%3A10651cd11fe5b327c38580e32a097a122255cf8e7d2728ccfb522ed2b8ee99af'
url = 'https://www.streamraiders.com/api/game/?cn=getCaptainsForSearch&userId=534264662v&isCaptain=0&gameDataVersion=b975633b5de0&command=getCaptainsForSearch&page=1&resultsPerPage=24&filters=%7B%22ambassadors%22%3A%22false%22%7D&seed=0&clientVersion=0.238.0&clientPlatform=WebGL'

# Set up headers with the authentication token
headers = {
    'Cookie': 'ACCESS_INFO={auth_token};',
    'User-Agent': user_agent
}

# Make the HTTP request
response = requests.get(url, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Print the response content
    print(response.json())
    
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}")
    print(response.text)

"""
