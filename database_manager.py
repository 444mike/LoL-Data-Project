import sqlite3
import pandas as pd

def create_database(db_name):
    """Create a new SQLite database with tables for match info, participants, and teams."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create match_info table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_info (
        matchId TEXT PRIMARY KEY,
        gameCreation INTEGER,
        gameDuration INTEGER,
        gameMode TEXT,
        gameType TEXT,
        gameVersion TEXT,
        mapId INTEGER,
        platformId TEXT,
        queueId INTEGER,
        tournamentCode TEXT
    )
    ''')
    
    # Create participants table
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
        PRIMARY KEY (matchId, participantId)
    )
    ''')
    
    # Create teams table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        teamId INTEGER,
        matchId TEXT,
        championId INTEGER,
        pickTurn INTEGER,
        PRIMARY KEY (matchId, pickTurn)
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {db_name} created with tables match_info, participants, and teams.")



def insert_data_from_excel(excel_file, db_name):
    """Insert data from an Excel file into the SQLite database."""
    # Read data from Excel sheets
    match_info_df = pd.read_excel(excel_file, sheet_name='Match Info')
    participants_df = pd.read_excel(excel_file, sheet_name='Participants')
    teams_df = pd.read_excel(excel_file, sheet_name='Teams')
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Insert match info data
    for index, record in match_info_df.iterrows():
        cursor.execute('''
        INSERT OR IGNORE INTO match_info (
            matchId, gameCreation, gameDuration, gameMode, gameType,
            gameVersion, mapId, platformId, queueId, tournamentCode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            record['matchId'], record['gameCreation'], record['gameDuration'],
            record['gameMode'], record['gameType'], record['gameVersion'],
            record['mapId'], record['platformId'], record['queueId'], record['tournamentCode']
        ))
    
    # Insert participants data
    for index, record in participants_df.iterrows():
        cursor.execute('''
        INSERT OR IGNORE INTO participants (
            participantId, matchId, puuid, championId, championName, champLevel,
            assists, deaths, kills, damageDealtToBuildings, goldEarned, individualPosition,
            item0, item1, item2, item3, item4, item5, item6, lane, riotIdGameName,
            riotIdTagline, role, win
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        ''', (
            record['participantId'], record['matchId'], record['puuid'],
            record['championId'], record['championName'], record['champLevel'],
            record['assists'], record['deaths'], record['kills'],
            record.get('damageDealtToBuildings', 0), record['goldEarned'],
            record.get('individualPosition'), record['item0'], record['item1'],
            record['item2'], record['item3'], record['item4'],
            record['item5'], record['item6'], record.get('lane'),
            record.get('riotIdGameName'), record.get('riotIdTagline'),
            record.get('role'), record['win']
        ))
    
    # Insert teams data
    for index, record in teams_df.iterrows():
        cursor.execute('''
        INSERT OR IGNORE INTO teams (
            teamId, matchId, championId, pickTurn
        ) VALUES (?, ?, ?, ?);
        ''', (
            record['teamId'], record['matchId'],
            record['championId'], record['pickTurn']
        ))

    conn.commit()
    conn.close()
    print(f"Data from {excel_file} inserted into {db_name}.")