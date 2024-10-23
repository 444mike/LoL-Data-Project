import requests
import time
import json
import pandas as pd

# servers = lil shitters
# regions = 4 regions (americas, asia, europe, sea)

api_key = "RGAPI-c74fe57b-d8ae-418d-b28d-3e7aa4ff2d16"
key = f"api_key={api_key}"

servers = {"br": "br1",
           "eune": "eun1",
           "euw": "euw1",
           "jp": "jp1",
           "kr": "kr",
           "la1": "la1",
           "la2": "la2",
           "na": "na1",
           "oc": "oc1",
           "tr": "tr1",
           "ru": "ru",
           "ph": "ph2",
           "sg": "sg2",
           "th": "th2",
           "tw": "tw2",
           "vn": "vn2"           
           }

def request(api_url):
    while True:
        resp = requests.get(api_url)
        if resp.status_code == 429:
            print("Sleeping")
            time.sleep(5)
            continue
        data = resp.json()
        return data
    
# List of fields to extract from each participant
desired_fields = [
    'assists', 'champLevel', 'championId', 'championName',
    'damageDealtToBuildings', 'deaths', 'goldEarned', 'individualPosition',
    'item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'kills',
    'lane', 'participantId', 'puuid', 'riotIdGameName', 'riotIdTagline',
    'role', 'win', 'perks.statPerks.defense', 'perks.statPerks.flex',
    'perks.statPerks.offense', 'perks.styles'
]

def extract_desired_fields(participant):
    # Create a dictionary to hold only the desired fields
    filtered_data = {field: participant.get(field, None) for field in desired_fields}
    return filtered_data

# get PUUID from riot username + tagline
def getPUUID(username, tagline):
    api_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
    api_url = api_url + username + '/' + tagline + '/?' + key
    data = request(api_url)
    return data["puuid"]