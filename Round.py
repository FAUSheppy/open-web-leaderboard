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
            self.winnerSideString = "Security"
            self.loserSideString = "Insurgent"
        else:
            self.winnerSideString = "Insurgent"
            self.loserSideString = "Security"
        if mapName:
            self.mapName = mapName
        else:
            self.mapName = "unavailiable"
        self.duration = datetime.timedelta(seconds=int(duration))
        if prediction == 0:
            self.prediction = self.winnerSideString
        elif prediction == 1:
            self.prediction = self.loserSideString
        else:
            self.prediction = "Error"
        self.confidence = int(confidence * 100)
