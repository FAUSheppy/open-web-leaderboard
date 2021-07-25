#!/usr/bin/python3

import riotwatcher
import json
import argparse
import os
import time
from jinja2 import Environment, FileSystemLoader
import requests

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

cache   = dict()
counter = 

def getCache():
    return cache

def getPlayerRatingFromApi(playerName, WATCHER):

    if playerName in cache:
        return cache[playerName]

    while(True):
        try:
            pTmp = WATCHER.summoner.by_name(REGION, playerName)
        except requests.exceptions.HTTPError as e:
            # not found #
            if e.response.status_code == 404:
                cache[playerName] = 0
                return 0
            # rate limit
            elif e.response.status_code == 429:
                print("Ratelimit reached")
                time.sleep(120)
                continue
            else:
                raise e
        if not pTmp:
            cache[playerName] = 0
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
            cache.update( { playerName : computed })

        return computed
