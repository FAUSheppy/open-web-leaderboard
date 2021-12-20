#!/usr/bin/python3
import flask
import requests
import argparse
import datetime
import itertools
import json
import os
import random
import secrets
import riotwatcher
import time
import statistics
import api


app = flask.Flask("open-leaderboard")

WATCHER = None
KEY     = None

if os.path.isfile("config.py"):
    app.config.from_object("config")

SEGMENT=100
SERVERS=list()

from sqlalchemy import Column, Integer, String, Boolean, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

POSITIONS_NAMES = ["Top", "Jungle", "Mid", "Bottom", "Support" ]
DATABASE_PRIO_NAMES = ["prioTop", "prioJungle", "prioMid", "prioBot", "prioSupport" ]
TYPE_JSON = 'application/json'

HTTP_OK = 200

class PlayerInDatabase(db.Model):
    __tablename__ = "players"
    player        = Column(String, primary_key=True)
    rating        = Column(Integer)
    ratingFix     = Column(Integer)
    lastUpdated   = Column(Integer)

class Submission(db.Model):
    __tablename__ = "submissions"
    ident         = Column(String, primary_key=True)
    submissionId  = Column(String)
    player        = Column(String)
    prioTop       = Column(Integer)
    prioJungle    = Column(Integer)
    prioMid       = Column(Integer)
    prioBot       = Column(Integer)
    prioSupport   = Column(Integer)

class Player:
    def __init__(self, name, prio):
        self.name = name
        self.prio = prio

@app.route("/role-submission", methods=['GET', 'POST'])
def roleSubmissionTool():

    submissionId = flask.request.args.get("id")
    player = flask.request.args.get("player")

    if flask.request.method == 'POST':

        submissionQuery = db.session.query(PlayerInDatabase)
        identKey = "{}-{}".format(submissionId, player)
        submission = submissionQuery.filter(PlayerInDatabase.ident == identKey).first()

        if not submission:
            submission = Submission(identKey, submissionId, player, -1, -1, -1, -1, -1)

        for i in range(0, 5):
            formKey = "prio_" + POSITIONS_NAMES[i]
            setattr(submission, DATABASE_PRIO_NAMES[i], flask.request.form[formKey])

        db.session.merge(submission)
        db.session.commit()

        return flask.redirect("/balance-tool?id=" + ident)
    else:
        return flask.render_template("role_submission.html", positions=positions, ident=ident)

@app.route("/balance-tool-data")
def balanceToolData():

    submissionId = flask.request.args.get("id")
    submissionsQuery = db.session.query(PlayerInDatabase)
    submissions = submissionsQuery.filter(PlayerInDatabase.submissionId == submissionId).all()

    if not submissions:
        return flask.Response(json.dumps({ "no-data" : False }), HTTP_OK, mimetype=TYPE_JSON)

    retDict.update()

    dicts = [ s.toDict() for s in submissions ]
    return flask.Response(json.dumps({ "submissions" : dicts }), HTTP_OK, mimetype=TYPE_JSON)


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

        import sys
        print(flask.request.json, file=sys.stderr)
        print(retDict, file=sys.stderr)
        renderContent = flask.render_template("balance_response_partial.html", d=retDict,
                                                reqJson=flask.request.json,
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

@app.route("/get-cache")
def getCacheLoc():
    return (json.dumps(api.getCache()), 200)

@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)

@app.before_first_request
def init():

    global WATCHER

    app.config["DB"] = db
    db.create_all()

    with open("key.txt","r") as f:
        key = f.read().strip()
        WATCHER = riotwatcher.LolWatcher(key)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start open-leaderboard', \
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--interface', default="localhost")
    parser.add_argument('--port', default="5002")
    
    args = parser.parse_args()

    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(host=args.interface, port=args.port)
