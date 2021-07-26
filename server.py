#!/usr/bin/python3
import flask
import requests
import argparse
import datetime
import flask_caching as fcache
import itertools
import json
import os
import MapSummary
import random
import secrets
import riotwatcher
import time
import statistics

from database import DatabaseConnection
import api


app = flask.Flask("open-leaderboard")

WATCHER = None
KEY     = None


if os.path.isfile("config.py"):
    app.config.from_object("config")

cache = fcache.Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

SEGMENT=100
SERVERS=list()



def prettifyMinMaxY(computedMin, computedMax):
    if computedMax > 0 and computedMin > 0:
        return (0, 4000)
    else:
        return (computedMin - 100, 4000)

@app.route("/players-online")
def playersOnline():
    '''Calc and return the online players'''

    playerTotal = 0
    error       = ""

    for s in SERVERS:
        try:
            with valve.source.a2s.ServerQuerier((args.host, args.port)) as server:
                playerTotal += int(server.info()["player_count"])
        except NoResponseError:
            error = "Server Unreachable"
        except Exception as e:
            error = str(e)

    retDict = { "player_total" : playerTotal, "error" : error }
    return flask.Response(json.dumps(retDict), 200, mimetype='application/json')
            
    

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
    elif r.blacklist:
        return ("Unavailable due to pending GDPR deletion request", 451)
    r = db.calcRatingChanges(r)

    if not r:
        return ("", 404)

    r.winners = sorted(r.winners, key=lambda p: p.participation, reverse=True)
    r.losers = sorted(r.losers, key=lambda p: p.participation, reverse=True)

    return flask.render_template("single_round.html", r=r) 

@app.route("/livegames")
def liveGames():
    '''Display info about a single round itdentified by it's timestamp'''

    db = DatabaseConnection(app.config["DB_PATH"])
    rounds = db.getLiveGames()
    return flask.render_template("livegames.html", liveGameRounds=rounds, noRounds=not bool(rounds))

@app.route("/maps")
def maps():
    '''Show an overview of maps'''
    
    db = DatabaseConnection(app.config["DB_PATH"])
    start = datetime.datetime.now() - datetime.timedelta(days=4000)
    end = datetime.datetime.now()
    rounds = db.roundsBetweenDates(start, end)
    distinctMaps = db.distinctMaps()
    maps = []
    for mapName in [ tupel[0]  for tupel in distinctMaps]:
        roundsWithMap = list(filter(lambda r: r.mapName == mapName , rounds))
        maps += [MapSummary.MapSummary(roundsWithMap)]

    allMaps = MapSummary.MapSummary(rounds)
    allMaps.mapName = "All Maps*"
    maps += [allMaps]
    

    mapsFiltered = filter(lambda x: x.mapName, maps)
    return flask.render_template("maps.html", maps=mapsFiltered)

@app.route("/rounds-by-timestamp")
@app.route("/rounds")
def rounds():
    '''Show rounds played on the server'''
    
    start = flask.request.args.get("start")
    end   = flask.request.args.get("end")
    
    if not start or not end:
        start = datetime.datetime.now() - datetime.timedelta(days=365)
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

class Player:
    def __init__(self, name, prio):
            self.name = name
            self.prio = prio

# TODO
submission = dict()
@app.route("/role-submission", methods=['GET', 'POST'])
def roleSubmissionTool():
    positions=["Top", "Jungle", "Mid", "Bottom", "Support" ]

    ident = flask.request.args.get("id")
    if flask.request.method == 'POST':

        if not ident in submission:
            submission.update({ ident : [] })
        
        tmp = dict()
        tmp.update({ "name" : flask.request.form["playername"] })
        for p in positions:
            tmp.update({ p : flask.request.form["prio_{}".format(p)] })

        existed = False
        for pl in submission[ident]:
            if pl["name"] == tmp["name"]:
                for p in positions:
                    pl.update({ p : flask.request.form["prio_{}".format(p)] })
                existed = True
                break;

        if not existed:
            submission[ident] += [tmp]

        return flask.redirect("/balance-tool?id={}".format(ident))
    else:
        return flask.render_template("role_submission.html", 
                                    positions=positions,
                                    ident=ident)

@app.route("/balance-tool-data")
def balanceToolData():
    ident = flask.request.args.get("id")
    retDict = dict()
    if not ident in submission:
        return flask.Response(json.dumps({ "no-data" : False }), 200, mimetype='application/json')
    retDict.update({ "submissions" : submission[ident] })
    return flask.Response(json.dumps(retDict), 200, mimetype='application/json')


@app.route('/')
@app.route("/balance-tool", methods=['GET', 'POST'])
def balanceTool():
    positions=["Top", "Jungle", "Mid", "Bottom", "Support"]

    #db = DatabaseConnection(app.config["DB_PATH"])

    if flask.request.method == 'POST':

        players = []
        threshold = 0.7
        for k,v in flask.request.json.items():
            if k == "acceptable-solution-threshold":
                threshold = v
                continue
            for i in range(5):
                if v[i] in positions:
                    v[i] = 5
                else:
                    v[i] = int(v[i])
            p = Player(k, v)
            players += [p]
        
        # theoretical minnimum #
        theoMin = sum([ min(p.prio) for p in players ])

        permutations = itertools.permutations(players)
        
        best = 100
        bestOption = None
        alternateOptions = []
        alternateOptionsAboveThreshold = []
        for option in permutations:
        
            cur = 0
            
            for i in range(len(option)):
                cur += option[i].prio[i%5]
       
            if theoMin/cur > threshold:
                alternateOptionsAboveThreshold.append(list(option))
            
            qualityCur = int(theoMin/cur*100)
            if cur < best:
                best = cur
                bestOption = list(option)
                alternateOptions = []
                alternateOptions.append(list(option))
                print("Option Found Quality: {}%".format(str(qualityCur)))
            elif cur == best or qualityCur > threshold*100:
                alternateOptions.append(list(option))
       
        alternateOptions += alternateOptionsAboveThreshold
        retDict = { "left" : {}, "right" : {} }
        bestOption = list(bestOption)
        if len(bestOption) < 10:
            for x in range(10-len(bestOption)):
                bestOption += [Player("", [0,0,0,0,0])]
        for o in alternateOptions:
            for x in range(10-len(o)):
                o += [Player("", [0,0,0,0,0])]

        # fix options with rating #
        bestOptionWithRating = None
        bestOptionRatings = None

        # alternate options rundown positional diff #
        posCurrDiff = 100000
        for o in alternateOptions:
            firstHalf = o[:5]
            secondHalf = o[5:]

            firstHalfVal    = [0, 0, 0, 0, 0]
            secondHalfVal   = [0, 0, 0, 0, 0]
          
            countFirstHalf = 0
            for pil in firstHalf:
                if pil:
                    firstHalfVal[countFirstHalf] = api.getPlayerRatingFromApi(pil.name, WATCHER)
                    #print(pil.name, firstHalfVal[countFirstHalf])
                countFirstHalf += 1

            countSecondHalf = 0
            for pil in secondHalf:
                if pil:
                    secondHalfVal[countSecondHalf] = api.getPlayerRatingFromApi(pil.name, WATCHER)
                    #print(pil.name, secondHalfVal[countSecondHalf])
                countSecondHalf += 1

            posDiff = abs(statistics.median(firstHalfVal) - statistics.median(secondHalfVal))

            # check if posdiff is better #
            if posDiff < posCurrDiff:
                bestOptionWithRating = o
                bestOptionRatings = firstHalfVal + secondHalfVal
                qualityRatings = -1

                # find the best permutation of this solution #
                for i in range(0,5):
                    teamDiff = abs(sum(firstHalfVal) - sum(secondHalfVal))

                    # first flip
                    tmp = firstHalfVal[i]
                    firstHalfVal[i] = secondHalfVal[i]
                    secondHalfVal[i] = tmp
                    teamDiffNew = abs(sum(firstHalfVal) - sum(secondHalfVal))
                    
                    # if new is not better #
                    if not (teamDiffNew < teamDiff):
                        # flip it back #
                        tmp = firstHalfVal[i]
                        firstHalfVal[i] = secondHalfVal[i]
                        secondHalfVal[i] = tmp
                    # else flip the names too #
                    else:
                        tmp = firstHalf[i]
                        firstHalf[i] = secondHalf[i]
                        secondHalf[i] = tmp
                        # and reset the option #
                        bestOptionWithRating = firstHalf + secondHalf
                        bestOptionRatings = firstHalfVal + secondHalfVal
                        qualityRatings = min(sum(firstHalfVal)/sum(secondHalfVal),
                                                sum(secondHalfVal)/sum(firstHalfVal))



        for i in range(5):
            retDict["left"].update( { positions[i] : bestOptionWithRating[i].name   })
            retDict["right"].update({ positions[i] : bestOptionWithRating[i+5].name })

        renderContent = flask.render_template("balance_response_partial.html", d=retDict,
                                                requests=flask.request.json,
                                                positions=positions,
                                                ratings=bestOptionRatings,
                                                qualityPositions=int(theoMin/best*100),
                                                qualityRatings=int(qualityRatings*100))
        return flask.Response(
                json.dumps({ "content": renderContent }), 200, mimetype='application/json')
    else:
        givenIdent = flask.request.args.get("id")
        if givenIdent:
            ident = givenIdent
        else:
            ident = secrets.token_urlsafe(16)
            return flask.redirect("/balance-tool?id={}".format(ident))
        return flask.render_template("json_builder.html", 
                                    positions=positions,
                                    sides=["left", "right"],
                                    ident=ident)
@app.route("/get-cache")
def getCacheLoc():
    return (json.dumps(api.getCache()), 200)

@app.route("/player-api")
def playerApi():
    result = api.getPlayerRatingFromApi(flask.request.args.get("id"), WATCHER)
    if result:
        return ("OK", 200)
    else:
        return ("Nope", 404)

@app.route("/player-api-cache")
def playerApiCache():
    result = api.checkPlayerKnown(flask.request.args.get("id"))
    if result and result[1] != 0:
        return ("OK", 200)
    else:
        return ("Nope", 404)

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
@cache.cached(timeout=10, query_string=True)
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

    playerList = None
    doNotComputeRank = True
    if playerName:
        playersInLeaderboard = db.findPlayerByName(playerName)
        if not playersInLeaderboard:
            cannotFindPlayer = flask.Markup("<div class=noPlayerFound>No player of that name</div>")
            start = 0
        else:
            if len(playersInLeaderboard) == 1:
                rank = playersInLeaderboard[0].rank
                if(playersInLeaderboard[0].games < 10):
                    return flask.redirect("/player?id={}".format(playersInLeaderboard[0].playerId))
                searchName = playersInLeaderboard[0].name
                start = rank - (rank % SEGMENT)
            else:
                playerList = playersInLeaderboard
                for p in playerList:
                    if p.rank == -1:
                        p.rankStr = "N/A"
                    else:
                        p.rankStr = str(p.rank)
                doNotComputeRank = False

    reachedEnd = False
    maxEntry = 0
    if not playerList:            
        # compute range #
        end = start + SEGMENT
        maxEntry = db.getTotalPlayers()
        reachedEnd = False
        if end > maxEntry:
            start = maxEntry - ( maxEntry % SEGMENT ) - 1
            end   = maxEntry - 1
            print(maxEntry)
            reachedEnd = True

        playerList = db.getRankRange(start, end)
    
    endOfBoardIndicator = ""
    if reachedEnd:
        endOfBoardHtml = "<div id='eof' class=endOfBoardIndicator> - - - End of Board - - - </div>"
        endOfBoardIndicator = flask.Markup(endOfBoardHtml)
    
    # fix <100 player start at 0 #
    if maxEntry <= 100:
        start = max(start, 0)
    
    finalResponse = flask.render_template("base.html", playerList=playerList, \
                                                        doNotComputeRank=doNotComputeRank, \
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

    global WATCHER
    with open("key.txt","r") as f:
        key = f.read().strip()
        WATCHER = riotwatcher.LolWatcher(key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start open-leaderboard', \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--interface', default="localhost", \
            help='Interface on which flask (this server) will take requests on')
    parser.add_argument('--port', default="5002", \
            help='Port on which flask (this server) will take requests on')

    parser.add_argument('--skillbird-db', required=False, help='skillbird database (overrides web connection if set)')
   
    
    args = parser.parse_args()
    app.config["DB_PATH"] = args.skillbird_db
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host=args.interface, port=args.port)
