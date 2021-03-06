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
        self.id = int(float(timestamp))
        self.winners = [ player.playerFromDict(wp, int(duration)) for wp in winnersParsed ]
        self.losers =  [ player.playerFromDict(lp, int(duration)) for lp in losersParsed  ]
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

        self.numericPrediction = prediction
        self.confidence = (int(confidence * 100) - 50)*2
        self.quality    = int(150 - self.confidence)
        if self.confidence < 50:
            self.prediction = "-"
        elif prediction == 0:
            self.prediction = self.winnerSideString
        elif prediction == 1:
            self.prediction = self.loserSideString
        else:
            self.prediction = "Error"
