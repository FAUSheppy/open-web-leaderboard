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
            averageSeconds = sum([t.total_seconds() for t  in self.times]) / len(self.times)
            self.averageTime = datetime.timedelta(seconds=int(averageSeconds))

            mapper = [ 1 if x == 0 else -1 for x in self.predictions ]
            reverseMapper = [ 1 if x == 0 else 0 for x in self.predictions ]
            self.ratingSystemDeviation = 0

            confidenceCutoff = 60
            confidenceTupels = list(filter(lambda x: x[1] > confidenceCutoff,
                                        zip(reverseMapper, self.confidence)))

            mapperTupels = list(filter(lambda x: x[1] > confidenceCutoff,
                                    zip(mapper, self.confidence)))

            for i in range(0, len(mapperTupels)):
                self.ratingSystemDeviation += mapperTupels[i][0] * max(100, 50+mapperTupels[i][1])

            self.ratingSystemDeviation /= len(mapperTupels)
            self.predictionCorrectPercentage  = sum([x[0] for x in confidenceTupels])
            self.predictionCorrectPercentage /= len(confidenceTupels)
            self.predictionCorrectPercentage *= 100
            self.predictionCorrectPercentage = round(self.predictionCorrectPercentage)

        except ZeroDivisionError:
            pass

