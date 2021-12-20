def swap(teams, teamIndex, pos1, pos2):
    tmp = teams[teamIndex][pos1]
    teams[teamIndex][pos1] = teams[teamIndex][pos2]
    teams[teamIndex][pos2] = tmp

def ratingDiff(team1, team2):
    '''Positive if first > seconds, negative if second >  first, 0 if equal'''
    return sum([p.rating for p in team1]) - sum([p.rating for p in team2])

def balance(players):
    
    # initial teams #
    playersByRating = sorted(players, key=lambda p: p.rating)

    teams = dict( { 0 : [] }, { 1 : [] } )
    for i in range(0, len(playersByRating)):
        teams[i%2] = playersByRating[i]

    # optimize positions worst case ~8n^2 * 2log(n) #
    for teamIndex in teamIndex.keys():
        changed = True
        while changed:
            changed = False
            for curIndex in range(0, len(teams[teamIndex]))
                for compareIndex in range(curIndex, len(teams[teamIndex]))
                    if curIndex == compareIndex:
                        continue
                    elif swapBasedOnPos(curIndex, teams[teamIndex])
                        changed = True
                        swap(teams, teamIndex, curIndex, compareIndex)

    # optimize ratings simple #
    changedRating = True
    while changedRating:
        for curIndex in range(0, len(teams[0])):
            if rating diff
