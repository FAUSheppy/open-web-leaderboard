#!/usr/bin/python3
import flask
import requests
import argparse
import flask_caching as fcache
import json
import database as db
import os


app = flask.Flask("open-leaderboard")

if os.path.isfile("config.py"):
    app.config.from_object("config")

cache = fcache.Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

SEGMENT=100

class PlayerInLeaderboard:
    def __init__(self, dbRow):
        '''Initialize a player object later to be serialized to HTML'''

        name, playerID, rating, games, wins = dbRow
       
        # set relevant values #
        self.name       = name
        self.playerID   = playerID
        self.rating     = int(float(rating))
        self.games      = int(games)
        self.wins       = int(wins)
        self.loses      = self.games - self.wins

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

        # mark returned string as preformated html #
        return flask.Markup(string)

@app.route('/leaderboard')
@app.route('/')
@cache.cached(timeout=600, query_string=True)
def leaderboard():
    '''Show main leaderboard page with range dependant on parameters'''

    # parse parameters #
    page        = flask.request.args.get("page")
    playerName  = flask.request.args.get("string")


    if page:
        start = SEGMENT * int(page)
    else:
        start = 0

    # handle find player request #
    cannotFindPlayer = ""
    searchName = ""

    if playerName:
        playersWithRankUrl = FIND_PLAYER.format(server=SERVER, pname=playerName)
        playersWithRank    = str(requests.get(playersWithRankUrl).content, "utf-8")
        print(playersWithRank)
        if playersWithRank == "[]":
            cannotFindPlayer = flask.Markup("<div class=noPlayerFound>No player of that name</div>")
            start = 0
        else:
            searchName = playersWithRank.split(",")[1].strip(" '")
            rank = int(playersWithRank.split(",")[4].strip(" ')]["))
            start = rank - (rank % SEGMENT)

    end = start + SEGMENT


    # compute range #
    maxEntry = db.getTotalPlayers(app.config["DB_PATH"])
    reachedEnd = False
    if end > maxEntry:
        start = maxEntry - ( maxEntry % SEGMENT ) - 1
        end   = maxEntry - 1
        reachedEnd = True

    playerList = db.getRankRange(app.config["DB_PATH"], start, end)

    columContent = flask.Markup(flask.render_template("playerLine.html", \
                                        playerRank="Rank", \
                                        playerName="Player", \
                                        playerRating="Rating", \
                                        playerGames="Games", \
                                        playerWinratio="Winratio"))
    
    endOfBoardIndicator = ""
    if reachedEnd:
        endOfBoardHtml = "<div id='eof' class=endOfBoardIndicator> - - - End of Board - - - </div>"
        endOfBoardIndicator = flask.Markup(endOfBoardHtml)
    
    # fix <100 player start at 0 #
    if maxEntry <= 100:
        start = max(start, 0)
    
    print(playerList)
    finalResponse = flask.render_template("base.html", playerList=playerList, \
                                                        columNames=columContent, \
                                                        start=start, \
                                                        endOfBoardIndicator=endOfBoardIndicator, \
                                                        findPlayer=cannotFindPlayer, \
                                                        searchName=searchName)
    return finalResponse

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.before_first_request
def init():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start open-leaderboard', \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--interface', default="localhost", \
            help='Interface on which flask (this server) will take requests on')
    parser.add_argument('--port', default="5002", \
            help='Port on which flask (this server) will take requests on')

    parser.add_argument('--skillbird-db', required=True, help='skillbird database (overrides web connection if set)')
   
    
    args = parser.parse_args()
    app.config["DB_PATH"] = args.skillbird_db
    app.run(host=args.interface, port=args.port)
