import json
import datetime

class Round:
    def __init__(self, dbRow):
        '''Create Round Object from cursor database row'''

        timestamp, winners, losers, winnerSide, mapName, duration, prediction, confidence = dbRow
        startTime = datetime.datetime.fromtimestamp(int(float(timestamp)))
        winnersParsed = json.loads(winners)
        losersParsed  = json.loads(losers)

        self.startTime = startTime
        self.winners = winners
        self.losers = losers
        self.winnerSide = winnerSide
        if winnerSide == 2:
            self.winnerSideString = "Insurgent"
        else:
            self.winnerSideString = "Security"
        self.mapName = mapName
        self.duration = datetime.timedelta(seconds=int(duration))
