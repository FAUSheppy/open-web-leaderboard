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
SEGMENT     = 100

class Player:
    def __init__(self, line):
        pass

    def getLineHTML(self):
        pass

@app.route('/leaderboard')
def leaderboard():
    '''Show main leaderboard page with range dependant on parameters'''

    # parse parameters #
    start = flask.request.args.get(PARAM_START)
    page  = flask.request.args.get("page")

    if start:
        start = int(start)
    elif page:
        start = SEGMENT * int(page)
    else:
        start = 0

    end = start + SEGMENT

    # request information from rating server #
    requestURL = BASE_URL.format(server=SERVER, \
                                    path=LOCATION, \
                                    paramStart=PARAM_START, \
                                    paramEnd=PARAM_END, \
                                    start=start, \
                                    end=end)

    response = str(requests.get(requestURL), "utf-8")

    # create relevant html-lines from player
    players      = [Player(line) for line in response.split("\n")]
    playersHTMLs = [p.getLineHTML() for p in players]

    # sanity check reponse #
    if len(players) > 100:
        raise ValueError("Bad reponse from rating server")

    # template html #
    leaderBoardColumnNames = "<div class=colum-names>{}</div>"
    leaderBoardEvenLine    = "<div class=line-even>{}</div>"
    leaderBoardOddLine     = "<div class=line-odd>{}</div>"

    columContent = "LOL"
    leaderBoardContent = leaderBoardColumnNames.format(columContent)
    
    for i in range(0, len(players)):
        if i%2 == 0:
            leaderBoardContent += leaderBoardEvenLine.format(players[i].getLineHTML())
        else:
            leaderBoardContent += leaderBoardOdd.format(players[i].getLineHTML())
    
    finalResponse = render_template("base.html", 
    return finalResponse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start open-leaderboard')
    parser.add_argument('--rating-server', default=SERVER, \
            help='Compatible rating server to query, default %(default)')
    parser.add_argument('--request-url', default=LOCATION, \
            help='API location for rating range, default %(default)')
    parser.add_argument('--param-start', default=PARAM_START, \
            help='Name of parameter annotating the start of the rating range, default %(default)')
    parser.add_argument('--param-end', default=PARAM_END, \
            help='Name of parameter annotating the end of the rating range, default %(default)')
    parser.add_argument('--interface', default="localhost", \
            help='Interface on which flask (this server) will take requests on, default %(default)')
    parser.add_argument('--port', default="5002", \
            help='Port on which flask (this server) will take requests on, default %(default)')
    args = parser.parse_args()

    SERVER      = args.rating_server
    LOCATION    = args.request_url
    PARAM_START = args.param_start
    PARAM_END   = args.param_end

    app.run(host=args.interface, port=args.port)
