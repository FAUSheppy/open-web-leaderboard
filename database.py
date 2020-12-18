#!/usr/bin/python3
import json
import sqlite3
import player
import os
import datetime
import Round

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
        cursor.execute("SELECT Count(*) FROM players where games >= 10 and not lastgame is null")
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
        sqlQuery = '''Select * FROM players where games >= 10
                        and not lastgame is null
                        ORDER BY (mu - 2*sigma) DESC LIMIT ? OFFSET ?'''
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

        # if there is exactly one hit for the exact name just return that #
        if row and not cursor.fetchone():
            p = player.PlayerInLeaderboard(row)
            p.rank = self.getPlayerRank(p)
            return [p]

        playerRows = []
        cursor.execute("SELECT * FROM players WHERE name LIKE ? ORDER BY games DESC", (playerNamePrepared,))
        count = 0
        for pr in cursor:
            if count > 50:
                break;
            p = player.PlayerInLeaderboard(pr)
            p.rank = self.getPlayerRank(p)
            playerRows += [p]
            count += 1
    
        return playerRows

    def getPlayerRank(self, player):
        '''Calculate player rank - a player rank may change rapidly and 
            can't and shouldn't be used to identify a player'''
    
        cursor = self.connPlayers.cursor()
        if(player.games < 10):
            return -1
        cursor.execute('''SELECT COUNT(*) from players where games >= 10 
                            and not lastgame is null
                            and (mu-2*sigma) > (?-2*?);''',
                            (player.mu, player.sigma))
        rank = cursor.fetchone()[0]
        return rank

    def roundsBetweenDates(self, start, end):
        '''Get rounds played between two times'''

        cursor = self.connRounds.cursor()
        cursor.execute('''SELECT * FROM rounds WHERE timestamp between ? and ? 
                            AND duration > 120.0
                            order by timestamp DESC''', (start.timestamp(), end.timestamp()))
        
        rounds = []
        for row in cursor:
            rounds += [Round.Round(row)]
        return rounds

    def calcRatingChanges(self, roundObj):
        '''Calculates and sets rating changes in the player objects of this round'''

        cursorHist = self.connHistorical.cursor()
        for p in roundObj.winners + roundObj.losers:
            cursorHist.execute('''SELECT count(*) FROM playerHistoricalData 
                                WHERE timestamp < ? AND id = ?''',
                                (roundObj.startTime.timestamp(), p.playerId))

            if(cursorHist.fetchone()[0] < 10):
                p.ratingChangeString = "Placements"
                continue

            cursorHist.execute('''SELECT mu,sima FROM playerHistoricalData 
                                WHERE timestamp < ? AND id = ? order by timestamp DESC LIMIT 1 ''',
                                (roundObj.startTime.timestamp(), p.playerId))
            tupelPrev = cursorHist.fetchone()
            cursorHist.execute('''SELECT mu,sima FROM playerHistoricalData
                                WHERE timestamp == ? AND id = ? LIMIT 1''', 
                                (roundObj.startTime.timestamp(), p.playerId))
            tupelAfter = cursorHist.fetchone()
            if tupelPrev and tupelAfter:
                muPrev, sigmaPrev = tupelPrev
                muAfter, sigmaAfter = tupelAfter
                p.mu = muPrev
                p.sigma = sigmaPrev
                p.muChange = muAfter - muPrev
                p.sigmaChange = sigmaAfter - sigmaPrev
                ratingChange = int( (muAfter-muPrev) - 2*(sigmaAfter-sigmaPrev) )
                if abs(ratingChange) > 500:
                    p.ratingChangeString = "N/A"
                    continue
                if(ratingChange < 0):
                    p.ratingChangeString = "- &nbsp;{:x>5}".format(abs(ratingChange))
                else:
                    p.ratingChangeString = "+ {:x>5}".format(ratingChange)
                p.ratingChangeString = p.ratingChangeString.replace("x", "&nbsp;")

        roundObj.invalid = ""
        roundObj.teamPtRatio = 0
        if roundObj.teamPtRatio > 2.1:
            roundObj.invalid += "Not rated because of playtime imbalance."
        if roundObj.duration < datetime.timedelta(seconds=120):
            if roundObj.invalid:
                roundObj.invalid += "<br>"
            roundObj.invalid += "Not rated because too short."

        return roundObj

    def getRoundByTimestamp(self, timestamp):
        '''Get a round by it's start time (more or less it primary key)'''

        cursorRounds = self.connRounds.cursor()
        cursorRounds.execute('''SELECT * from rounds where timestamp = ?''', (timestamp,))
        row = cursorRounds.fetchone()
        if not row:
            return None
        return Round.Round(row)

    def distinctMaps(self):
        '''Get all distinct maps from rounds database'''
        cursorRounds = self.connRounds.cursor()
        return cursorRounds.execute('''SELECT DISTINCT map from rounds''')

