#!/usr/bin/python3
import flask
import requests
import argparse


app = flask.Flask("open-leaderboard")

SERVER      = "localhost:5000"
LOCATION    = "/rankrange"
PARAM_START = "start"
PARAM_END   = "end"

BASE_URL    = "http://{server}{path}?{paramStart}={start}&{paramEnd}={end}"
MAX_ENTRY   = "http://{server}/getmaxentries"
FIND_PLAYER = "http://{server}/findplayer?string={pname}"
SEGMENT     = 100
SEPERATOR   = ','

class Player:
    def __init__(self, line):
        '''Initialize a player object later to be serialized to HTML'''

        # parse input line #
        try:
            name, playerID, rating, games, wins = line.split(SEPERATOR)
        except ValueError as e:
            print("Failed to parse line: {}".format(line))
            raise e
       
        # set relevant values #
        self.name     = name
        self.playerID = playerID
        self.rating   = int(float(rating))
        self.games    = int(games)
        self.wins     = int(wins)
        self.loses    = self.games - self.wins

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
        
def requestRange(start, end):
    '''Request a range from the rating server'''

    # request information from rating server #
    requestURL = BASE_URL.format(server=SERVER, \
                                    path=LOCATION, \
                                    paramStart=PARAM_START, \
                                    paramEnd=PARAM_END, \
                                    start=start, \
                                    end=end)

    return str(requests.get(requestURL).content, "utf-8")

@app.route('/leaderboard')
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
    if playerName:
        playersWithRankUrl = FIND_PLAYER.format(server=SERVER, pname=playerName)
        playersWithRank    = str(requests.get(playersWithRankUrl).content, "utf-8").split("\n")

        if len(playersWithRank) == 1 and playersWithRank[0] == "":
            cannotFindPlayer = flask.Markup("<div class=noPlayerFound>No player of that name</div>")
            start = 0
        elif len(playersWithRank) == 1:
            rank = int(playersWithRank[0].split(SEPERATOR)[-1])
            start = rank - (rank % SEGMENT)
        else:
            rank = int(playersWithRank[0].split(SEPERATOR)[-1])
            start = rank - (rank % SEGMENT)

    end = start + SEGMENT


    # request and check if we are within range #
    maxEntryUrl = MAX_ENTRY.format(server=SERVER)
    maxEntry = int(requests.get(maxEntryUrl).content)
    reachedEnd = False
    if end > maxEntry:
        start = maxEntry - ( maxEntry % SEGMENT ) - 1
        end   = maxEntry - 1
        reachedEnd = True

    # do the actual request #
    responseString = requestRange(start, end)

    # create relevant html-lines from player
    players      = [Player(line) for line in responseString.split("\n")]

    # sanity check reponse #
    if len(players) > 100:
        raise ValueError("Bad reponse from rating server")

    columContent = flask.Markup(flask.render_template("playerLine.html", \
                                        playerRank="Rank", \
                                        playerName="Player", \
                                        playerRatin="Rating", \
                                        playerGames="Games", \
                                        playerWinratio="Winratio"))
    
    endOfBoardIndicator = ""
    if reachedEnd:
        endOfBoardHtml = "<div id='eof' class=endOfBoardIndicator> - - - End of Board - - - </div>"
        endOfBoardIndicator = flask.Markup(endOfBoardHtml)
    
    finalResponse = flask.render_template("base.html", playerList=players, \
                                                        columNames=columContent, \
                                                        start=start, \
                                                        endOfBoardIndicator=endOfBoardIndicator, \
                                                        findPlayer=cannotFindPlayer)
    return finalResponse

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start open-leaderboard', \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--rating-server', default=SERVER, \
            help='Compatible rating server to query')
    parser.add_argument('--request-url', default=LOCATION, \
            help='API location for rating range')
    parser.add_argument('--param-start', default=PARAM_START, \
            help='Name of parameter annotating the start of the rating range')
    parser.add_argument('--param-end', default=PARAM_END, \
            help='Name of parameter annotating the end of the rating range')
    parser.add_argument('--interface', default="localhost", \
            help='Interface on which flask (this server) will take requests on')
    parser.add_argument('--port', default="5002", \
            help='Port on which flask (this server) will take requests on')
    args = parser.parse_args()

    SERVER      = args.rating_server
    LOCATION    = args.request_url
    PARAM_START = args.param_start
    PARAM_END   = args.param_end

    app.run(host=args.interface, port=args.port)
