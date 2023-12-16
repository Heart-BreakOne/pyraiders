import requests

def calculate_placement(url):
    #Things will happen here.
    res = requests.get(url)
    parsed_map = res.json()
    print(type(res))
    
    pass