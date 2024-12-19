import sqlite3
import pandas as pd

def create_database(db_name='lol_matches.db'):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the match_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_info (
            matchId TEXT PRIMARY KEY,
            dataVersion TEXT,
            gameCreation INTEGER,
            gameDuration INTEGER,
            gameEndTimestamp INTEGER,
            gameId INTEGER,
            gameMode TEXT,
            gameName TEXT,
            gameStartTimestamp INTEGER,
            gameType TEXT,
            gameVersion TEXT,
            mapId INTEGER,
            platformId TEXT,
            queueId INTEGER,
            tournamentCode TEXT
        );
    ''')

    # Create the participants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            participantId INTEGER,
            matchId TEXT,
            puuid TEXT,
            championId INTEGER,
            championName TEXT,
            champLevel INTEGER,
            assists INTEGER,
            deaths INTEGER,
            kills INTEGER,
            damageDealtToBuildings INTEGER,
            goldEarned INTEGER,
            individualPosition TEXT,
            item0 INTEGER,
            item1 INTEGER,
            item2 INTEGER,
            item3 INTEGER,
            item4 INTEGER,
            item5 INTEGER,
            item6 INTEGER,
            lane TEXT,
            riotIdGameName TEXT,
            riotIdTagline TEXT,
            role TEXT,
            win BOOLEAN,
            PRIMARY KEY (matchId, participantId),
            FOREIGN KEY (matchId) REFERENCES match_info(matchId)
        );
    ''')

    # Create the teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            matchId TEXT,
            teamId INTEGER,
            championId INTEGER,
            pickTurn INTEGER,
            PRIMARY KEY (matchId, teamId, pickTurn),
            FOREIGN KEY (matchId) REFERENCES match_info(matchId)
        );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f'Database {db_name} created with tables match_info, participants, and teams.')

def insert_data_from_excel(db_name='lol_matches.db', excel_file='matchinfo_NA1_5136694416.xlsx'):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Read data from Excel
    match_info_df = pd.read_excel(excel_file, sheet_name='Match Info')
    participants_df = pd.read_excel(excel_file, sheet_name='Participants')
    teams_df = pd.read_excel(excel_file, sheet_name='Teams')

    # Get the matchId from the Match Info sheet (assuming one row)
    match_id = match_info_df.iloc[0]['matchId']

    # Insert data into the match_info table
    match_info_record = match_info_df.iloc[0].to_dict()
    cursor.execute('''
        INSERT OR IGNORE INTO match_info (
            dataVersion, matchId, gameDuration, gameEndTimestamp, gameMode,
            gameName, gameStartTimestamp, gameType, gameVersion, mapId, platformId,
            queueId, tournamentCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (
        match_info_record['dataVersion'], match_info_record['matchId'],
        match_info_record['gameDuration'], match_info_record['gameEndTimestamp'],
        match_info_record['gameMode'], match_info_record['gameName'],
        match_info_record['gameStartTimestamp'], match_info_record['gameType'],
        match_info_record['gameVersion'], match_info_record['mapId'],
        match_info_record['platformId'], match_info_record['queueId'],
        match_info_record['tournamentCode']
    ))

    # Insert data into the participants table with the matchId
    participants_records = participants_df.to_dict(orient='records')
    for record in participants_records:
        cursor.execute('''
            INSERT OR IGNORE INTO participants (
                participantId, matchId, puuid, championId, championName, champLevel,
                assists, deaths, kills, damageDealtToBuildings, goldEarned, individualPosition,
                item0, item1, item2, item3, item4, item5, item6, lane, riotIdGameName,
                riotIdTagline, role, win
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            record['participantId'], match_id, record['puuid'], record['championId'],
            record['championName'], record['champLevel'], record['assists'], record['deaths'],
            record['kills'], record['damageDealtToBuildings'], record['goldEarned'],
            record['individualPosition'], record['item0'], record['item1'], record['item2'],
            record['item3'], record['item4'], record['item5'], record['item6'],
            record['lane'], record['riotIdGameName'], record['riotIdTagline'], record['role'], record['win']
        ))

    # Insert data into the teams table with the matchId
    teams_records = teams_df.to_dict(orient='records')
    for record in teams_records:
        cursor.execute('''
            INSERT OR IGNORE INTO teams (
                matchId, teamId, championId, pickTurn
            ) VALUES (?, ?, ?, ?);
        ''', (
            match_id, record['teamId'], record['championId'], record['pickTurn']
        ))

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print(f'Data from {excel_file} inserted into {db_name} successfully using INSERT OR IGNORE.')



def insert_match_data(match_info, db_name='lol_matches.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Extract data from match_info JSON and insert into appropriate tables.
    match_id = match_info['metadata']['matchId']
    # Extract and insert match-level info
    cursor.execute('''
        INSERT OR IGNORE INTO match_info (
            dataVersion, matchId, gameCreation, gameDuration, gameEndTimestamp,
            gameMode, gameName, gameStartTimestamp, gameType, gameVersion, mapId,
            platformId, queueId, tournamentCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (
        match_info['metadata']['dataVersion'], match_id,
        match_info['info']['gameCreation'], match_info['info']['gameDuration'],
        match_info['info']['gameEndTimestamp'], match_info['info']['gameMode'],
        match_info['info']['gameName'], match_info['info']['gameStartTimestamp'],
        match_info['info']['gameType'], match_info['info']['gameVersion'],
        match_info['info']['mapId'], match_info['info']['platformId'],
        match_info['info']['queueId'], match_info['info'].get('tournamentCode')
    ))

    # Insert participant and team data similarly...
    # Example for inserting participants (adjust as needed)
    for participant in match_info['info']['participants']:
        cursor.execute('''
            INSERT OR IGNORE INTO participants (
                participantId, matchId, puuid, championId, championName, champLevel,
                assists, deaths, kills, damageDealtToBuildings, goldEarned, individualPosition,
                item0, item1, item2, item3, item4, item5, item6, lane, riotIdGameName,
                riotIdTagline, role, win
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            participant['participantId'], match_id, participant['puuid'],
            participant['championId'], participant['championName'], participant['champLevel'],
            participant['assists'], participant['deaths'], participant['kills'],
            participant.get('damageDealtToBuildings', 0), participant['goldEarned'],
            participant.get('individualPosition'), participant['item0'], participant['item1'],
            participant['item2'], participant['item3'], participant['item4'],
            participant['item5'], participant['item6'], participant.get('lane'),
            participant.get('riotIdGameName'), participant.get('riotIdTagline'),
            participant.get('role'), participant['win']
        ))

    # Insert team data into the teams table
    for team in match_info['info']['teams']:
        for ban in team.get('bans', []):
            cursor.execute('''
                INSERT OR IGNORE INTO teams (
                    matchId, teamId, championId, pickTurn
                ) VALUES (?, ?, ?, ?);
            ''', (
                match_id, team['teamId'], ban['championId'], ban['pickTurn']
            ))

    # Don't forget to commit and close the connection
    conn.commit()
    conn.close()
    print(f'Match data for match ID {match_id} inserted into {db_name}.')

def get_data(query, db_path='/home/4444mike/mysite/lol_matches.db'):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df



# Example usage:
# insert_data_from_excel(excel_file='matchinfo_NA1_5136694416.xlsx')


# Example usage:
#create_database()





