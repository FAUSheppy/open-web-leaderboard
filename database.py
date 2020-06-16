#!/usr/bin/python3
import json
import sqlite3
import player

DB_BASE = "file:{}?mode=ro"

def getTotalPlayers(database):
    '''Get the total number of players in the database'''

    print(DB_BASE.format(database))
    conn = sqlite3.connect(DB_BASE.format(database), uri=True)
    cursor = conn.cursor()
    cursor.execute("SELECT Count(*) FROM players")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def getRankRange(database, start, end):
    '''Get a range of players by rank'''

    conn = sqlite3.connect(DB_BASE.format(database), uri=True)
    cursor = conn.cursor()
    limit = end - start
    cursor.execute("Select * FROM players ORDER BY (mu - 2*sigma) DESC LIMIT ? OFFSET ?", (limit, start))
    rows = cursor.fetchall()
    conn.close()
    playerList = []
    for row in rows:
        playerList += [player.PlayerInLeaderboard(row)]

    return playerList

def findPlayerByName(playerName):
    '''Find a player by his name (prefer fullmatch)'''

    conn = sqlite3.connect(DB_BASE.format(database), uri=True)
    cursor = conn.cursor()
    playerNamePrepared = "%{}%".format(playerName.replace("%", "%%"))
    cursor.execute("SELECT * FROM players WHERE name == ?", (playerName,))
    row = cursor.fetone()

    playerRow = None
    if row:
        cursor.execute("SELECT * FROM players WHERE name LIKE ?", (playerNamePrepared,))
        row = cursor.fetchone()[0]
        if not row:
            conn.close()
            return None

    conn.close()
    return players.Leaderboard(playerRow)
