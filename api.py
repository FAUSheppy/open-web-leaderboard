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

def tierToNumber(tier):
    ratingmap = {   'CHALLENGER' : 3500,
                    'GRANDMASTER': 3000,
                    'MASTER'     : 2500,
                    'DIAMOND'    : 2000,
                    'PLATINUM'   : 1500,
                    'GOLD'       : 500,
                    'SILVER'     : 0,
                    'BRONZE'     : -500,
                    'IRON'       : -1000 }
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
        print("sqlite cache player not found")
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
    conn.close()
        

def getPlayerRatingFromApi(playerName, WATCHER):

    if not playerName:
        return 0

    tupel = checkPlayerKnown(playerName)
    if tupel:
        return tupel[1]

    while(True):
        try:
            pTmp = WATCHER.summoner.by_name(REGION, playerName)
        except requests.exceptions.HTTPError as e:
            # not found #
            if e.response.status_code == 404:
                addToDB(playerName, 0)
                return 0
            # rate limit
            elif e.response.status_code == 429:
                print("Ratelimit reached")
                time.sleep(120)
                continue
            else:
                raise e
        if not pTmp:
            addToDB(playerName, 0)
            return 0

        computed = 0
        
        try:
            pInfo = WATCHER.league.by_summoner(REGION, pTmp["id"])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("Ratelimit reached")
                time.sleep(120)
                continue
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
