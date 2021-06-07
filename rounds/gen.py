#!/usr/bin/python3

winnerside = input("Winnerseide (0/1 , 0=bue, 1=red): ")
duration = input("Duration: ")
duration = int(duration.split(":")[0])*60+int(duration.split(":")[1])

print("Blue Team")
blueTeam = []
for i in range(5):
    pname = input("Name: ")
    p = dict()
    p.update({"playerId" : pname})
    p.update({"isFake" : False})
    blueTeam += [p]

print("Red Team")
redTeam = []
for i in range(5):
    pname = input("Name: ")
    p = dict()
    p.update({"playerId" : pname})
    p.update({"isFake" : False})
    redTeam += [p]

if winnerside == 0:
    winners = blueTeam
    losers = redTeam
else:
    winners = redTeam
    losers = blueTeam

startTime = input("Start Time: ")

retDict = {}
retDict.update({ "map" : "SR" })
retDict.update({ "winner-side" : winnerside })
retDict.update({ "winners" : winners})
retDict.update({ "losers" : losers})
retDict.update({ "duration" : duration })
retDict.update({ "startTime" : startTime})

import json
print()
print(json.dumps(retDict, indent=4, sort_keys=False))
