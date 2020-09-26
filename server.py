#!/usr/bin/python3
import flask
import requests
import argparse
import flask_caching as fcache
import json
import os

from database import DatabaseConnection


app = flask.Flask("open-leaderboard")

if os.path.isfile("config.py"):
    app.config.from_object("config")

cache = fcache.Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

SEGMENT=100

@app.route('/playerdata')
def playerInfo():
    '''API-Endpoint for Canvas Query'''

    playerId = flask.request.args.get("id")

    db = DatabaseConnection(app.config["DB_PATH"])
    data = db.getHistoricalForPlayerId(playerId)

    return json.dumps(data)

@app.route("/player")
def player():
    '''Show Info about Player'''

    db = DatabaseConnection(app.config["DB_PATH"])
    player = db.getPlayerById(playerId)
    player.rank = db.getPlayerRank(player)

    return flask.render_template("player.html", player=player)

@app.route('/leaderboard')
@app.route('/')
@cache.cached(timeout=600, query_string=True)
def leaderboard():
    '''Show main leaderboard page with range dependant on parameters'''

    # parse parameters #
    page        = flask.request.args.get("page")
    playerName  = flask.request.args.get("string")
    db = DatabaseConnection(app.config["DB_PATH"])

    if page:
        start = SEGMENT * int(page)
    else:
        start = 0

    # handle find player request #
    cannotFindPlayer = ""
    searchName = ""

    if playerName:
        playerInLeaderboard, rank = db.findPlayerByName(playerName)
        if not playerInLeaderboard:
            cannotFindPlayer = flask.Markup("<div class=noPlayerFound>No player of that name</div>")
            start = 0
        else:
            searchName = playerInLeaderboard.name
            start = rank - (rank % SEGMENT)

    end = start + SEGMENT


    # compute range #
    maxEntry = db.getTotalPlayers()
    reachedEnd = False
    if end > maxEntry:
        start = maxEntry - ( maxEntry % SEGMENT ) - 1
        end   = maxEntry - 1
        reachedEnd = True

    playerList = db.getRankRange(start, end)

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
