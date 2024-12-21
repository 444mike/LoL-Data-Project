# Import everything from RiotAPI and database_manager
from api.riotAPI import *
from database_manager import *
import os


def process_matches_from_file(match_ids_file, region, db_name='lol_matches.db'):
    # Step 1: Read match IDs from the JSON file
    with open(match_ids_file, 'r') as file:
        match_ids = json.load(file)
    print(f"Loaded {len(match_ids)} match IDs from {match_ids_file}")

    # Step 2: Loop through each match ID
    for match_id in match_ids:
        try:
            print(f"Processing match ID: {match_id}")

            # Step 3: Retrieve match info
            match_info = getMatchInfo(match_id, region)

            # Step 4: Insert match data into the database directly
            insert_match_data(match_info, db_name)

            print(f"Successfully processed match ID: {match_id}")

        except Exception as e:
            print(f"Error processing match ID {match_id}: {e}")

    print("Finished processing all match IDs.")


def process_matches_from_file_test(match_ids_file, region, db_name='lol_matches.db'):
    # Step 1: Read match IDs from the JSON file
    with open(match_ids_file, 'r') as file:
        match_ids = json.load(file)
    print(f"Loaded {len(match_ids)} match IDs from {match_ids_file}")

    # Step 2: Loop through each match ID
    for i in range(1900, 4700):
        try:
            print(f"Processing match ID: {match_ids[i]}")

            # Step 3: Retrieve match info
            match_info = getMatchInfo(match_ids[i], region)

            # Step 4: Insert match data into the database directly
            insert_match_data(match_info, db_name)

            print(f"Successfully processed match ID: {match_ids[i]}")

        except Exception as e:
            print(f"Error processing match ID {match_ids[i]}: {e}")

    print("Finished processing all match IDs.")

# Example usage:
# Replace 'matchids.json' with the path to your JSON file containing match IDs.
# Replace 'americas' with the correct region for your API calls.
if __name__ == '__main__':
    process_matches_from_file('grandmasterMatchIds_na1.json', 'americas', 'lol_matches.db')

