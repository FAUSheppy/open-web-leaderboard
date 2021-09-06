#!/usr/bin/python3

import riotwatcher
import json
import argparse
import os
import time
from jinja2 import Environment, FileSystemLoader
import requests
import datetime as dt
import sqlite3

REGION  = "euw1"
DEFAULT_RATING = 1200

def tierToNumber(tier):
    ratingmap = {   'CHALLENGER' : 4500,
                    'GRANDMASTER': 4000,
                    'MASTER'     : 3500,
                    'DIAMOND'    : 3000,
                    'PLATINUM'   : 2500,
                    'GOLD'       : 1500,
                    'SILVER'     : 1000,
                    'BRONZE'     : 500,
                    'IRON'       : 0 }
    return ratingmap[tier]

def divisionToNumber(division):
    divisionmap = { "I"   : 300,
                    "II"  : 200,
                    "III" : 100,
                    "IV"  : 0 }
    return divisionmap[division]

DATABASE = "rating_cache.sqlite"
def checkPlayerKnown(playerName):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    backlog = dt.datetime.now() - dt.timedelta(days=7)
    query = '''SELECT * from players where playerName = ? LIMIT 1;'''
    cursor.execute(query, (playerName,))
    try:
        playerName, rating, lastUpdated = cursor.fetchone()
    except TypeError:
        print("sqlite cache '{}' not found".format(playerName))
        return None
    conn.close()
    return (playerName, rating, lastUpdated)

def addToDB(playerName, rating):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO players VALUES(?,?,?);",(
                                        playerName,
                                        rating,
                                        dt.datetime.now().timestamp()))
    conn.commit()
    print("Added {}".format(playerName))
    conn.close()
        

def getPlayerRatingFromApi(playerName, WATCHER):

    if not playerName:
        return DEFAULT_RATING

    tupel = checkPlayerKnown(playerName)
    if tupel:
        return tupel[1]

    while(True):
        try:
            pTmp = WATCHER.summoner.by_name(REGION, playerName)
        except requests.exceptions.HTTPError as e:
            # not found #
            if e.response.status_code == 404:
                addToDB(playerName, DEFAULT_RATING)
                return DEFAULT_RATING
            # rate limit
            elif e.response.status_code == 429:
                print("Ratelimit reached")
                #time.sleep(120)
                #continue
                return DEFAULT_RATING
            else:
                raise e
        if not pTmp:
            addToDB(playerName, 0)
            return DEFAULT_RATING

        computed = DEFAULT_RATING
        
        try:
            pInfo = WATCHER.league.by_summoner(REGION, pTmp["id"])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Ratelimit reached")
                return DEFAULT_RATING
                #time.sleep(120)
                #continue
            else:
                raise e

        for queue in pInfo:
            if queue["queueType"] != "RANKED_SOLO_5x5":
                continue
            computed = tierToNumber(queue["tier"]) + divisionToNumber(queue["rank"]) + \
                                    int(queue["leaguePoints"])
            print(computed)

        addToDB(playerName, computed)
        return computed
