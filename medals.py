import flask
import markupsafe

medalDict = {   "games-played-1" : { "name" : "Tourist", 
                                        "text" : "Played {} games on this server", 
                                        "color" : "white",
                                        "text-color" : "black" },

                "games-played-2" : { "name" : "Enlisted", 
                                        "text" : "Played {} games on this server",
                                        "color": "green",
                                        "text-color" : "white" },

                "games-played-3" : { "name" : "Veteran",
                                        "text" : "Played {} games on this server",
                                        "color" : "yellow",
                                        "text-color" : "black" },

                "games-played-4" : { "name" : "Alpha Chad",
                                        "text" : "Played {} games on this server",
                                        "color" : "black",
                                        "text-color" : "red" },

                "rating-cur-1" :   { "name" : "Slightly skilled",
                                        "text" : "Rated above 1500",
                                        "color" : "beige",
                                        "text-color" : "black" },

                "rating-2k-1" :   { "name" : "Contender",
                                        "text" : "Played {} games above 2000 rating",
                                        "color" : "coral",
                                        "text-color" : "black" },
                "rating-2k-2" :   { "name" : "Known Contender",
                                        "text" : "Played {} games above 2000 rating",
                                        "color" : "lightgreen",
                                        "text-color" : "black" },
                "rating-2k-3" :   { "name" : "Epic Backup",
                                        "text" : "Played {} games above 2000 rating",
                                        "color" : "darkgreen",
                                        "text-color" : "white" },

                "rating-3k-1" :   { "name" : "Epic",
                                        "text" : "Played {} games above 3000 rating",
                                        "color" : "lightblue",
                                        "text-color" : "black" },
                "rating-3k-2" :   { "name" : "Legend",
                                        "text" : "Played {} games above 3000 rating",
                                        "color" : "orange",
                                        "text-color" : "black" },
                "rating-3k-3" :   { "name" : "All Along The Watchtower",
                                        "text" : "???",
                                        "color" : "red",
                                        "text-color" : "black" },
                "rating-3k-4" :   { "name" : "Highlander",
                                        "text" : "There can only be one.",
                                        "color" : "darkred",
                                        "text-color" : "white" }
                }

def medalGen(medal, formatInsert=None):
    '''Gen HTML for metal'''
    html = '\
            <div style="background-color: {bg} !important; color: {color} !important;"\
                class="btn btn-secondary"\
                data-toggle="tooltip" data-placement="top" title="{tooltip}">\
                {text}\
            </div>\
            '
    tmp = html.format(bg=medal["color"], tooltip=medal["text"], text=medal["name"],
                        color=medal["text-color"])
    if formatInsert:
        tmp = tmp.format(formatInsert)
    return markupsafe.Markup(tmp)

def getMedals(ratingList, gamesPlayed, currentRating):
    '''Get Medals this player should have'''
    medals = []

    if gamesPlayed > 2000:
        medals += [medalGen(medalDict["games-played-4"], gamesPlayed)]
    elif gamesPlayed > 500:
        medals += [medalGen(medalDict["games-played-3"], gamesPlayed)]
    elif gamesPlayed > 100:
        medals += [medalGen(medalDict["games-played-2"], gamesPlayed)]
    elif gamesPlayed > 50:
        medals += [medalGen(medalDict["games-played-1"], gamesPlayed)]

    games2k = len(list(filter(lambda x: x > 2000, ratingList)))
    games3k = len(list(filter(lambda x: x > 3000, ratingList)))

    if games2k > 1000:
        medals += [medalGen(medalDict["rating-2k-3"], games2k)]
    elif games2k > 100:
        medals += [medalGen(medalDict["rating-2k-2"], games2k)]
    elif games2k > 0:
        medals += [medalGen(medalDict["rating-2k-1"], games2k)]
    
    if games3k > 350:
        medals += [medalGen(medalDict["rating-3k-4"], games3k)]
    if games3k > 200:
        medals += [medalGen(medalDict["rating-3k-3"], games3k)]
    if games3k > 50:
        medals += [medalGen(medalDict["rating-3k-2"], games3k)]
    if games3k > 5:
        medals += [medalGen(medalDict["rating-3k-1"], games3k)]
       
    if currentRating > 1500:
        medals += [medalGen(medalDict["rating-cur-1"])]

    return medals
