from riotAPI import getListOfChallengerPlayers, getListOfGrandmasterPlayers, getMatchIDs, getMatchInfo
from database_manager import insert_match_data
import json


def save_grandmaster_and_challenger_puuids(server, output_file):
    try:
        # Step 1: Fetch Challenger PUUIDs
        print("Fetching Challenger players...")
        challenger_puuids = getListOfChallengerPlayers(server)
        print(f"Retrieved {len(challenger_puuids)} Challenger PUUIDs.")

        # Step 2: Fetch Grandmaster PUUIDs
        print("Fetching Grandmaster players...")
        grandmaster_puuids = getListOfGrandmasterPlayers(server)
        print(f"Retrieved {len(grandmaster_puuids)} Grandmaster PUUIDs.")

        # Step 3: Combine both lists and remove duplicates
        combined_puuids = list(set(challenger_puuids + grandmaster_puuids))
        print(f"Combined total unique PUUIDs: {len(combined_puuids)}")

        # Step 4: Save to JSON file
        with open(output_file, 'w') as file:
            json.dump(combined_puuids, file, indent=4)

        print(f"Saved {len(combined_puuids)} unique PUUIDs to {output_file}")

    except Exception as e:
        print(f"Error: {e}")



def fetch_match_ids(puuid_file, output_file, region, games_per_player=20):
    # Step 1: Load PUUIDs from the input file
    with open(puuid_file, 'r') as file:
        puuids = json.load(file)

    print(f"Loaded {len(puuids)} PUUIDs. Fetching match IDs...")

    # Step 2: Loop through PUUIDs and fetch match IDs
    all_match_ids = []
    for i, puuid in enumerate(puuids):
        try:
            print(f"Fetching match IDs for player {i+1}/{len(puuids)}")
            match_ids = getMatchIDs(region, puuid, str(games_per_player))
            all_match_ids.extend(match_ids)  # Add match IDs to the list

        except Exception as e:
            print(f"Error fetching match IDs for PUUID {puuid}: {e}")

    # Step 3: Remove duplicate match IDs
    unique_match_ids = list(set(all_match_ids))
    print(f"Retrieved {len(unique_match_ids)} unique match IDs.")

    # Step 4: Save match IDs to a JSON file
    with open(output_file, 'w') as file:
        json.dump(unique_match_ids, file, indent=4)

    print(f"Match IDs saved to {output_file}")



def load_match_data_to_db(match_ids_file, region, db_name):
    # Step 1: Load match IDs from the JSON file
    with open(match_ids_file, 'r') as file:
        match_ids = json.load(file)
    
    print(f"Loaded {len(match_ids)} match IDs. Processing...")

    # Step 2: Loop through each match ID and insert into the database
    for i, match_id in enumerate(match_ids):
        try:
            print(f"Fetching match info for match {i+1}/{len(match_ids)}: {match_id}")
            match_info = getMatchInfo(match_id, region)

            # Step 3: Insert match data into the database
            insert_match_data(match_info, db_name)
            print(f"Successfully inserted match {i+1}/{len(match_ids)}")

        except Exception as e:
            print(f"Error processing match ID {match_id}: {e}")
            continue  # Skip to the next match ID

    print("Finished processing all match IDs.")

# Example usage
if __name__ == "__main__":
    match_ids_file = "grandmaster_challengerMatchIds_na1.json"  # File with match IDs
    region = "americas"  # Replace with the correct region
    db_name = "lol_matches.db"  # Your SQLite database name

    load_match_data_to_db(match_ids_file, region, db_name)


