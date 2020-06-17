#!/usr/bin/python3
import json
import sqlite3
import player

DB_BASE = "file:{}?mode=ro"

def getTotalPlayers(database):
    '''Get the total number of players in the database'''

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

def findPlayerByName(database, playerName):
    '''Find a player by his name (prefer fullmatch)'''

    conn = sqlite3.connect(DB_BASE.format(database), uri=True)
    cursor = conn.cursor()
    playerNamePrepared = "%{}%".format(playerName.replace("%", "%%"))
    cursor.execute("SELECT * FROM players WHERE name == ?", (playerName,))
    row = cursor.fetchone()

    playerRow = None
    if row:
        cursor.execute("SELECT * FROM players WHERE name LIKE ?", (playerNamePrepared,))
        playerRow = cursor.fetchone()
        if not playerRow:
            conn.close()
            return (None, None)

    playerInLeaderboard = player.PlayerInLeaderboard(playerRow)
    # compte rank
    cursor.execute("SELECT COUNT(*) from players where (mu-2*sigma) > (?-2*?);",
                        (playerInLeaderboard.mu, playerInLeaderboard.sigma))
    rank = cursor.fetchone()[0]
    conn.close()
    return (playerInLeaderboard, rank)
