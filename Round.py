import json
import datetime
import player

class Round:
    def __init__(self, dbRow):
        '''Create Round Object from cursor database row'''

        timestamp, winners, losers, winnerSide, mapName, duration, prediction, confidence = dbRow
        startTime = datetime.datetime.fromtimestamp(int(float(timestamp)))
        winnersParsed = json.loads(winners)
        losersParsed  = json.loads(losers)

        self.startTime = startTime
        self.winners = [ player.playerFromDict(wp) for wp in winnersParsed ]
        self.losers =  [ player.playerFromDict(lp) for lp in losersParsed  ]
        self.winnerSide = winnerSide
        self.duration = datetime.timedelta(seconds=int(duration))

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

        self.confidence = int(confidence * 100)
        self.numericPrediction = prediction
        if prediction == 0:
            self.prediction = self.winnerSideString
        elif prediction == 1:
            self.prediction = self.loserSideString
        else:
            self.prediction = "Error"
