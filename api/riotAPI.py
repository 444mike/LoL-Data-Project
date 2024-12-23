import requests
import time
import json
import pandas as pd

# servers = lil shitters
# regions = 4 regions (americas, asia, europe, sea)

api_key = "RGAPI-748451c6-475a-4bb0-87af-cfebe6ca6cb8"
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

def getListOfChallengerPlayers(server):
    listOfChallengerPlayersPuuid = []
    api_url = "https://" + server + ".api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?" + key
    data = request(api_url)
    players = data["entries"]
    for player in players:
        summonerID = player["summonerId"]
        puuid = convertSummonerIDtoPUUID(server, summonerID)
        listOfChallengerPlayersPuuid.append(puuid)
        print(listOfChallengerPlayersPuuid)
    return listOfChallengerPlayersPuuid

def getListOfGrandmasterPlayers(server):
    listOfGrandmasterPlayersPuuid = []
    api_url = "https://" + server + ".api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?" + key
    data = request(api_url)
    players = data["entries"]
    for player in players:
        summonerID = player["summonerId"]
        puuid = convertSummonerIDtoPUUID(server, summonerID)
        listOfGrandmasterPlayersPuuid.append(puuid)
    return listOfGrandmasterPlayersPuuid

def getListOfMasterPlayers(server):
    listOfMasterPlayersPuuid = []
    api_url = "https://" + server + ".api.riotgames.com/lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5?" + key
    data = request(api_url)
    players = data["entries"]
    counter = 0
    for player in players:
        summonerID = player["summonerId"]
        puuid = convertSummonerIDtoPUUID(server, summonerID)
        listOfMasterPlayersPuuid.append(puuid)
        counter += 1
        print(counter)

    return listOfMasterPlayersPuuid

def getListOfMasterPlusPlayers(server):
    a = getListOfChallengerPlayers(server)
    b = getListOfGrandmasterPlayers(server)
    c = getListOfMasterPlayers(server)
    listOfMasterPlusPlayers = a + b + c
    return listOfMasterPlusPlayers

def getMatchIDs(region, puuid, numberOfGames):
    api_url = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids?queue=420&type=ranked&count=" + numberOfGames + "&" + key
    data = request(api_url)
    print(data)
    return data

def getMatchInfo(matchid, region):
    api_url = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + matchid + "?" + key
    data = request(api_url)
    return data

def getMatchTimelineInfo(matchid, region):
    api_url = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + matchid + "/timeline" + "?" + key
    data = request(api_url)
    return data

def getPatchOfMatch(matchid, region):
    api_url = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + matchid + "?" + key
    data = request(api_url)
    patch = data["info"]["gameVersion"]
    return patch

def convertSummonerIDtoPUUID(server, summonerID):
    api_url = "https://" + server + ".api.riotgames.com/lol/summoner/v4/summoners/" + summonerID + "?" + key
    data = request(api_url)
    puuid = data["puuid"]
    return puuid

def createFileOfChallengerPlayers(server):
    challenger_puuids = getListOfChallengerPlayers("na1")
    # Specify the file name where you want to save the data.
    output_file = "challengerPlayers_na1.json"

    # Write the list of PUUIDs to the JSON file.
    with open(output_file, "w") as file:
        json.dump(challenger_puuids, file, indent=4)

    print(f"Challenger players saved to {output_file}")


def createFileOfGrandmasterPlayers(server):
    grandmaster_puuids = getListOfGrandmasterPlayers(server)
    # Specify the file name where you want to save the data.
    output_file = "grandmasterPuuids_na1.json"

    # Write the list of PUUIDs to the JSON file.
    with open(output_file, "w") as file:
        json.dump(grandmaster_puuids, file, indent=4)

    print(f"Grandmaster players saved to {output_file}")

def createFileOfMasterPlayers(server):
    master_puuids = getListOfMasterPlayers(server)
    # Specify the file name where you want to save the data.
    output_file = "masterPuuids_na1.json"

    # Write the list of PUUIDs to the JSON file.
    with open(output_file, "w") as file:
        json.dump(master_puuids, file, indent=4)

    print(f"Master players saved to {output_file}")

def json_to_excel(json_file_path, excel_file_path):
    # Convert JSON data to an Excel file
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    # Flatten and normalize the data as needed
    info_data = data.get('info', {})
    participants = info_data.get('participants', [])
    participants_df = pd.json_normalize(participants)

    # Save to Excel file
    participants_df.to_excel(excel_file_path, index=False)
    print(f"Match info saved to {excel_file_path}")



challengerFile = "challengerPuuids_na1.json"
# with a list of challengerPuuids, get the matches

def getChallengerMatchIds(challengerFile, region, numberOfGames):
    # open file
    with open("challengerPuuids_na1.json", 'r') as file:
        challengers = json.load(file)

    # loop through and get past x amount of games for each player
    listOfChallengerMatchIds = []
    for challenger in challengers:
        listOfChallengerMatchIds.extend(getMatchIDs(region, challenger, numberOfGames))

    # write to json file
    with open("challengerMatchIds.json", 'w') as outfile:
        json.dump(listOfChallengerMatchIds, outfile, indent=4)
    return listOfChallengerMatchIds


def getMatchIds(rankPuuids, rankMatchIds, region, numberOfGames):
    # open file
    with open(rankPuuids, 'r') as file:
        puuids = json.load(file)

    # loop through and get past x amount of games for each player
    listOfMatchIds = []
    for puuid in puuids:
        listOfMatchIds.extend(getMatchIDs(region, puuid, numberOfGames))

    # write to json file
    with open(rankMatchIds, 'w') as outfile:
        json.dump(listOfMatchIds, outfile, indent=4)
    return listOfMatchIds


# given a match id and a server, convert the match_id json into an xlsx file
def create_flattened_match_excel(match_id, server):
    # Step 1: Retrieve the match info (replace with your actual function to get match data)
    match_info = getMatchInfo(match_id, server)  # Use your data retrieval function here
    
    # Step 2: Extract and flatten metadata and info
    metadata = match_info.get('metadata', {})
    info = match_info.get('info', {})
    
    # Create a copy of info without 'participants' and 'teams' for the metadata sheet
    info_for_metadata = info.copy()
    info_for_metadata.pop('participants', None)
    info_for_metadata.pop('teams', None)
    
    # Flatten metadata and the modified info data into a single dictionary
    flattened_metadata_info = {**metadata, **info_for_metadata}
    
    # Convert the flattened match-level data into a DataFrame with one row
    match_info_df = pd.DataFrame([flattened_metadata_info])
    print("Match Info DataFrame shape:", match_info_df.shape)
    
    # Step 3: Extract and flatten the specific fields from participants
    participants = info.get('participants', [])
    participants_fields = [
        'assists', 'champLevel', 'championId', 'championName', 'damageDealtToBuildings',
        'deaths', 'goldEarned', 'individualPosition', 'item0', 'item1', 'item2', 'item3', 
        'item4', 'item5', 'item6', 'kills', 'lane', 'participantId', 'puuid', 
        'riotIdGameName', 'riotIdTagline', 'role', 'totalDamageDealtToChampions', 'win',
        'perks.statPerks.defense', 'perks.statPerks.flex', 'perks.statPerks.offense', 'perks.styles'
    ]
    
    # Flatten participants data using json_normalize
    participants_flattened = pd.json_normalize(participants, sep='_')
    existing_fields = [field for field in participants_fields if field in participants_flattened.columns]
    participants_flattened = participants_flattened[existing_fields]
    print("Participants DataFrame shape:", participants_flattened.shape)
    
    # Step 4: Extract and flatten the team bans
    teams = info.get('teams', [])
    teams_flattened = pd.json_normalize(
        teams, 
        record_path='bans', 
        meta=['teamId'], 
        sep='_'
    )
    print("Teams DataFrame shape:", teams_flattened.shape)
    
    # Step 5: Save everything to an Excel file with multiple sheets
    excel_file_name = f"matchinfo_{match_id}.xlsx"
    with pd.ExcelWriter(excel_file_name) as writer:
        match_info_df.to_excel(writer, sheet_name='Match Info', index=False)
        participants_flattened.to_excel(writer, sheet_name='Participants', index=False)
        teams_flattened.to_excel(writer, sheet_name='Teams', index=False)
    
    print(f"Match info saved to {excel_file_name}")


if __name__ == '__main__':
    getMatchIds("grandmasterPuuids_na1.json", "grandmasterMatchIds_na1.json", "americas", "20")


