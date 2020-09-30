#!/usr/bin/python3
import flask
import requests
import argparse
import datetime
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



def prettifyMinMaxY(computedMin, computedMax):
    if computedMax > 0 and computedMin > 0:
        return (0, 4000)
    else:
        return (computedMin - 100, 4000)

@app.route("/round-info")
def singleRound():
    '''Display info about a single round itdentified by it's timestamp'''

    timestamp = flask.request.args.get("id")
    if not timestamp:
        return ("ID Missing", 404)
    if not timestamp.endswith(".0"):
        timestamp = timestamp + ".0"
    db = DatabaseConnection(app.config["DB_PATH"])
    r = db.getRoundByTimestamp(timestamp)
    if not r:
        return ("Round not found", 404)
    r = db.calcRatingChanges(r)

    if not r:
        return ("", 404)

    r.winners = sorted(r.winners, key=lambda p: p.participation, reverse=True)
    r.losers = sorted(r.losers, key=lambda p: p.participation, reverse=True)

    return flask.render_template("single_round.html", r=r) 

@app.route("/rounds-by-timestamp")
@app.route("/rounds")
def rounds():
    '''Show rounds played on the server'''
    
    start = flask.request.args.get("start")
    end   = flask.request.args.get("end")
    
    if not start or not end:
        start = datetime.datetime.now() - datetime.timedelta(days=7)
        end   = datetime.datetime.now()
    else:
        start = datetime.datetime.fromtimestamp(start)
        end   = datetime.datetime.fromtimestamp(end)
    
    db = DatabaseConnection(app.config["DB_PATH"])
    rounds = db.roundsBetweenDates(start, end)

    return flask.render_template("rounds.html", rounds=rounds)


    # get timestamp
    # display players
    # display rating change
    # display outcome
    # display map

@app.route("/player")
def player():
    '''Show Info about Player'''

    playerId = flask.request.args.get("id")
    if(not playerId):
        return ("", 404)

    db = DatabaseConnection(app.config["DB_PATH"])
    player = db.getPlayerById(playerId)

    if(not player):
        return ("", 404)

    player.rank = db.getPlayerRank(player)
    histData = db.getHistoricalForPlayerId(playerId)

    csv_month_year = []
    csv_ratings = []
    csv_timestamps = []

    minRating = 3000
    maxRating = 0

    if histData:
        datapoints = histData[playerId]
        if datapoints:

            tickCounter = 10
            for dpk in datapoints.keys():
                t = datetime.datetime.fromtimestamp(int(float(dpk)))
                tsMs = str(int(t.timestamp() * 1000))
                ratingString = str(int(datapoints[dpk]["mu"]) - 2*int(datapoints[dpk]["sigma"]))
                ratingAmored = '{ x : ' + tsMs + ', y : ' + ratingString + '}'
                csv_timestamps += [str(tsMs)]
                csv_ratings += [ratingAmored]
                
                tickCounter -= 1
                if tickCounter <= 0:
                    tickCounter = 10
                    csv_month_year += ['new Date({})'.format(tsMs)]

                minRating = min(minRating, int(ratingString))
                maxRating = max(maxRating, int(ratingString))

    yMin, yMax = prettifyMinMaxY(minRating, maxRating)
    
    # change displayed rank to start from 1 :)
    player.rank += 1

    return flask.render_template("player.html", player=player, CSV_RATINGS=",".join(csv_ratings), 
                                    CSV_MONTH_YEAR_OF_RATINGS=",".join(csv_month_year),
                                    CSV_TIMESTAMPS=csv_timestamps,
                                    Y_MIN=yMin, Y_MAX=yMax)

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
        pageInt = int(page)
        if pageInt < 0:
            pageInt = 0
        start = SEGMENT * int(page)
    else:
        pageInt = 0
        start = 0

    # handle find player request #
    cannotFindPlayer = ""
    searchName = ""

    if playerName:
        playerInLeaderboard = db.findPlayerByName(playerName)
        if not playerInLeaderboard:
            cannotFindPlayer = flask.Markup("<div class=noPlayerFound>No player of that name</div>")
            start = 0
        else:
            rank = playerInLeaderboard.rank
            if(playerInLeaderboard.games < 10):
                return flask.redirect("/player?id={}".format(playerInLeaderboard.playerId))
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
                                                        searchName=searchName,
                                                        nextPageNumber=int(pageInt)+1,
                                                        prevPageNumber=int(pageInt)-1)
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
