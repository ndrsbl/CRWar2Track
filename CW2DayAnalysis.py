# War 2 analysis: going through partner clans and for all check
# last 25 battles, how many are war, and show win ratio, etc.

from datetime import datetime, timedelta
import requests
import json
import itertools
import CRLib as cr
import CRIO as cri


riverClanTags = ["JP8VUC","2Q9JYY9J", cr.clanTagHW, "29R0YQ09", "8UUP909U"]

class ClanData:
    def __init__(self):
        self.battlesWon = 0
        self.battlesPlayed = 0


# The stats for a single player, war day won, lost, 
class PlayerStats:
    def __init__(self):
        self.name = ""
        self.battlesWon = 0
        self.battlesPlayed = 0
        self.boatAttacks = 0
        self.limitedInfo = False # only the last 25 games are available!!, this is true if first game is after war day start

def getWarStartPrefix():
    today = datetime.utcnow()
    # before 10 am gmt look for the previous day :)
    today = today - timedelta(hours=10)
    timestamp = today.strftime("%Y%m%d")
    if today.isoweekday == 1: # Monday, start of river race -> we look at 9:30
        timestamp += "T0930"
    else:
        timestamp += "T1000"
    return timestamp

# Per player gather war battles, and update clan level player stats
def populateWarGames(playerTag, startTime, player):
    r2=requests.get("https://api.clashroyale.com/v1/players/%23"+playerTag+"/battlelog", 
    headers = {"Accept":"application/json", "authorization":cr.auth}, 
    params = {"limit":100})
    battles = r2.json()
    # if playerTag == "R0LPRUJ":
    #     print (json.dumps(battles, indent = 2))
        # Types are: (NOT complete, there may be many others)
        # boatBattle
        # casual1v1
        # casual2v2
        # challenge
        # clanMate
        # clanMate2v2
        # friendly
        # None
        # PvP
        # riverRaceDuel
        # riverRacePvP
        # riverRaceDuelColosseum
        # get the last timestamp (battles are newest first)
    if len(battles) > 0:
        b = battles[-1]
        if startTime < b["battleTime"]: # this should be the oldest game
            # TODO: CR returns a lot of garbage: it sometimes includes ancient boat battles. Could filter these out?
            player[playerTag].limitedInfo = True

    for b in battles:
        #print("%s %s %s"%(b["battleTime"], b["team"][0]["name"],b["type"]))
        #print(json.dumps(b, indent = 2))

        battleType = b["type"]
        if((battleType=="riverRaceDuel"  
            or battleType=="riverRaceDuelColosseum"  
            or battleType=="riverRacePvP" 
            or battleType=="boatBattle") and startTime < b["battleTime"]):
            #print (json.dumps(b, indent = 2))
            #print("%s %s"%(b["battleTime"], b["type"]))

            # opponent -> crowns (compare???), team [0] crowns???

            if battleType=="riverRaceDuel" or battleType == "riverRaceDuelColosseum": 
                defenderCrown = b["team"][0]["crowns"]
                opponentCrown = b["opponent"][0]["crowns"]
                # print("%s %s by %s  %s:%s"%(b["battleTime"], b["type"], cr.getPlayerName(playerTag),defenderCrown, opponentCrown))
                # print("Team Card length:%s" % len(b["team"][0]["cards"]))
                gameCount = len(b["team"][0]["cards"]) / 8
                if(defenderCrown>opponentCrown): # won the duel
                   player[playerTag].battlesWon += gameCount
                player[playerTag].battlesPlayed += gameCount
                
                
            elif battleType=="riverRacePvP":
                defenderCrown = b["team"][0]["crowns"]
                opponentCrown = b["opponent"][0]["crowns"]
                if(defenderCrown>opponentCrown): # won the battle
                    player[playerTag].battlesWon += 1
                player[playerTag].battlesPlayed += 1 

            else: # boatBattle
                player[playerTag].battlesPlayed += 1
                player[playerTag].boatAttacks += 1


# Iterate through clan members, collect clan level stats, incomplete games, player stats
# results are saved, and information gathering is resumed if the call is run again
def getPlayerStats(ct, warStartTime):

    # Check if there is already a saved state available
    # TODO: control via option
    # TODO: log!
    rv = cri.loadGameState(ct, warStartTime)
    if rv is not None:
        (ts, ps) = rv
    else:
        ts, ps = warStartTime, dict()

    dataCollectedAt = datetime.utcnow().strftime("%Y%m%dT%H%M") # for serialization later

    # populate the player data from supercel
    for m in cr.clanMemberTags(ct):
        if not m in ps:
            ps[m] = PlayerStats()
        populateWarGames(m, ts, ps)

    # serialize the data and save
    cri.saveGameState(ct, warStartTime, dataCollectedAt, ps)

    return ps


# Print clan's statistics for the war day (participant numbers, win ratio)
def printClanWarDayStats(ct, playerStats):
    cd = ClanData()
    clanName = cr.getClanName(ct)
    for key, value in playerStats.items():
        cd.battlesWon += value.battlesWon
        cd.battlesPlayed += value.battlesPlayed

    if cd.battlesPlayed == 0:
        winRatio = 0
    else:        
        winRatio = round(100*cd.battlesWon/cd.battlesPlayed,2)

    print("%s: %s war battles played, %s won (%s%% win rate), %s members participated"%
        (clanName,cd.battlesPlayed, cd.battlesWon, winRatio, len(playerStats)))

# Print the players and the number of war games completed during the active war two day
def printWhoHasIncompleteGames(ct, playerStats):
    for key, value in sorted(playerStats.items(), reverse=True, key=lambda item: item[1].battlesPlayed):
        if value.limitedInfo:
            caveatMsg = "25+ games since war start"
        else:
            caveatMsg = ""
        print("%s: %s %s" % (cr.getPlayerName(key),int(value.battlesPlayed), caveatMsg))



warStartTime = getWarStartPrefix()
# warStartTime = "20210125T0930"
# warStartTime = "20210127T1000"
print("War day start is: %s" % warStartTime )

pss = getPlayerStats(cr.clanTagHW, warStartTime)
printWhoHasIncompleteGames(cr.clanTagHW, pss)


# printClanWarDayStats(cr.clanTagHW, pss)
# pss = getPlayerStats("29R0YQ09", warStartTime)
# printClanWarDayStats("29R0YQ09", pss)
