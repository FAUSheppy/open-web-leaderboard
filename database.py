#!/usr/bin/python3
import json
import sqlite3
import player
import os

DATABASE_PLAYERS    = "players.sqlite"
DATABASE_ROUNDS     = "rounds.sqlite"
DATABASE_HISTORICAL = "players.sqlite"

class DatabaseConnection:
    def __init__(self, basepath):
        self.dbFormatString = "file:{}?mode=ro"
        self.databasePlayers = self.dbFormatString.format(os.path.join(basepath, DATABASE_PLAYERS))
        self.databaseRounds = self.dbFormatString.format(os.path.join(basepath, DATABASE_ROUNDS))
        self.databaseHistorical = self.dbFormatString.format(
                                    os.path.join(basepath, DATABASE_HISTORICAL))

        self.connPlayers = sqlite3.connect(self.databasePlayers, uri=True)
        self.connRounds = sqlite3.connect(self.databaseRounds, uri=True)
        self.connHistorical = sqlite3.connect(self.databaseHistorical, uri=True)

    def __del__(self):
        self.connPlayers.close();
        self.connRounds.close();
        self.connHistorical.close();

    def getTotalPlayers(self):
        '''Get the total number of players in the database'''

        cursor = self.connPlayers.cursor()
        cursor.execute("SELECT Count(*) FROM players")
        count = cursor.fetchone()[0]
        return count

    def getHistoricalForPlayerId(self, playerId):
        '''Get historical data for a player'''

        cursor = self.connHistorical.cursor()
        cursor.execute("SELECT * FROM playerHistoricalData where id = ? order by timestamp ASC", (playerId,))
        rows = cursor.fetchall()

        PLAYER_ID = 0
        TIMESTAMP = 1
        MU = 2
        SIGMA = 3

        playerIdDict = dict()
        for r in rows:
            timestampDict = dict()
            timestampDict.update({ "mu" : r[MU] })
            timestampDict.update({ "sigma" : r[SIGMA]})
            playerIdDict.update({ r[TIMESTAMP] : timestampDict })

        try:
            retDict = { rows[0][PLAYER_ID] : playerIdDict }
        except IndexError:
            retDict = None
        return retDict

    def getPlayerById(self, playerId):
        '''Get a player by his id'''

        cursor = self.connPlayers.cursor()
        cursor.execute("SELECT * FROM players where id = ?", (playerId,))
        row = cursor.fetchone()

        if(row):
            playerInLeaderboard = player.PlayerInLeaderboard(row)
        else:
            playerInLeaderboard = None

        return playerInLeaderboard

    def getRankRange(self, start, end):
        '''Get a range of players by rank'''
    
        cursor = self.connPlayers.cursor()
        limit = end - start
        sqlQuery = "Select * FROM players ORDER BY (mu - 2*sigma) DESC LIMIT ? OFFSET ?"
        cursor.execute(sqlQuery, (limit, start))
        rows = cursor.fetchall()
        playerList = []
        for row in rows:
            playerList += [player.PlayerInLeaderboard(row)]
        return playerList

    def findPlayerByName(self, playerName):
        '''Find a player by his name (prefer fullmatch)'''
    
        cursor = self.connPlayers.cursor()
        playerNamePrepared = "%{}%".format(playerName.replace("%", "%%"))
        cursor.execute("SELECT * FROM players WHERE name == ?", (playerName,))
        row = cursor.fetchone()
    
        playerRow = None
        if not playerRow:
            cursor.execute("SELECT * FROM players WHERE name LIKE ?", (playerNamePrepared,))
            playerRow = cursor.fetchone()
            if not playerRow:
                conn.close()
                return (None, None)
    
        playerInLeaderboard = player.PlayerInLeaderboard(playerRow)
        playerInLeaderboard.rank = self.getPlayerRank(playerInLeaderboard)
        return playerInLeaderboard

    def getPlayerRank(self, player):
        '''Calculate player rank - a player rank may change rapidly and 
            can't and shouldn't be used to identify a player'''
    
        cursor = self.connPlayers.cursor()
        cursor.execute("SELECT COUNT(*) from players where (mu-2*sigma) > (?-2*?);",
                            (player.mu, player.sigma))
        rank = cursor.fetchone()[0]
        return rank
