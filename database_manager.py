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