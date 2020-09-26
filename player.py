#!/usr/bin/python3
import flask

class PlayerInLeaderboard:
    def __init__(self, dbRow):
        '''Initialize a player object later to be serialized to HTML'''

        playerId, name, lastGame, wins, mu, sigma, games = dbRow
       
        # set relevant values #
        self.name       = name
        self.playerId   = playerId
        self.mu         = mu
        self.sigma      = sigma
        self.rating     = int(self.mu) - 2*int(self.sigma)
        self.games      = int(games)
        self.wins       = int(wins)
        self.loses      = self.games - self.wins
        self.rank       = None

        # determine winratio #
        if self.games == 0:
            self.winratio = "N/A"
        else:
            self.winratio = str(int(self.wins/self.games * 100))

    def getLineHTML(self, rank):
        '''Build a single line for a specific player in the leaderboard'''

        string = flask.render_template("playerLine.html", \
                                        playerRank = rank, \
                                        playerName = self.name, \
                                        playerRating = self.rating, \
                                        playerGames = self.games, \
                                        playerWinratio = self.winratio)

        return flask.Markup(string)
