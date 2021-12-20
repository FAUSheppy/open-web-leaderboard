from constants import *

NO_CHANGE = -1

def shouldSwapBasedOnPrio(teams, curIndex, compareIndex, curTeamIndex):
    '''Return a team ID in which to switch with the compare index'''

    otherTeam = (curTeamIndex + 1) % 2

    curPrio = teams[curTeamIndex].affinityFor(curIndex)
    compPrioOtherTeam = teams[otherTeam].affinityFor(compareIndex)
    compPrioSameTeam = team[otherTeam].affinityFor(compareIndex)

    if curPrio > compPrioSameTeam and compPrioSameTeam > compPrioOtherTeam:
        return compPrioSameTeam
    elif curPrio > compPrioOtherTeam:
        return compPrioOtherTeam
    else:
        return NO_CHANGE

def swap(teams, teamIndex1, teamIndex2, pos1, pos2):
    '''Swap two positions in the same or different teams'''

    tmp = teams[teamIndex1][pos1]
    teams[teamIndex1][pos1] = teams[teamIndex2][pos2]
    teams[teamIndex2][pos2] = tmp

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
    for teamIndex in teams.keys():
        changed = True
        while changed:
            changed = False
            for curIndex in range(0, 5)
                for compareIndex in range(curIndex, 5)
                    if curIndex == compareIndex:
                        continue

                    # shouldSwap return -1 for no swap or the team to swap with #
                    swapTeam = shouldSwapBasedOnPrio(teams, curIndex, compareIndex, teamIndex)
                elif VALID_INDEX(swapTeam):
                        changed = True
                        swap(teams, teamIndex, swapTeam, curIndex, compareIndex)
    
    # optimize team rating #
    changedRating = True
    while changedRating:
        
        diff = ratingDiff(teams[0], teams[1])
        diffByPos = [ teams[0][i] - teams[1][i] for i in range(0, 5) ]

        for i in range(0, diffByPos):
            diffHelper = abs(diffByPos[i]-diff)
            if  diffHelper < 
        for curIndex in range(0, len(teams[0])):
            if rating diff
