import json
import datetime
import player
import datetime

class MapSummary:
    def __init__(self, rounds):
        '''Create a map MapSummary from a Round-Array'''

        self.securityWins = 0
        self.insurgentWins = 0
        self.times = []
        self.predictions = []
        self.totalGames = 0
        self.confidence = []
        self.mapName = None

        for r in rounds:
            self.mapName = r.mapName
            self.totalGames += 1
            if r.winnerSideString == "Insurgent":
                self.insurgentWins += 1
            else:
                self.securityWins += 1

            self.predictions += [r.numericPrediction]
            self.confidence += [r.confidence]
            self.times += [r.duration]
       
        self.insurgentWinPercent = ""
        self.securityWinPercent = ""
        self.ratingSystemDeviation = "-"
        self.averageTime = ""

        try:
            self.insurgentWinPercent = self.insurgentWins / self.totalGames*100
            self.securityWinPercent = self.securityWins / self.totalGames*100
            predictionPercision = 1 - sum(self.predictions)/len(self.predictions)
            confidenceAverage = sum(self.confidence) / len(self.confidence)
            averageSeconds = sum([t.total_seconds() for t  in self.times]) / len(self.times)
            self.averageTime = datetime.timedelta(seconds=int(averageSeconds))
            self.ratingSystemDeviation = predictionPercision*100 - confidenceAverage
        except ZeroDivisionError:
            pass

