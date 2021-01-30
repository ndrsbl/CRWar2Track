# War 2 analysis: going through partner clans and for all check
# last 25 battles, how many are war, and show win ratio, etc.

from datetime import datetime, timedelta
import requests
import json
import itertools
import CRLib as cr
import CRIO as cri
import sys

class CROptions:
    def __init__(self):
        self.freshData = False # Do not read saved state from the data directory
        self.readOnly = False # Persist battles into the data directory
        self.debugBattles = False # Internal, debug battles (CR keeps changing things for the war!)

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
def populateWarGames(playerTag, startTime, player, ct, o):
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
        if o.debugBattles:
            print("%s %s %s"%(b["battleTime"], b["team"][0]["name"],b["type"]))
        #print(json.dumps(b, indent = 2))

        battleType = b["type"]
        if((battleType=="riverRaceDuel"  
            or battleType=="riverRaceDuelColosseum"  
            or battleType=="riverRacePvP" 
            or battleType=="boatBattle") and startTime < b["battleTime"]):
            #print (json.dumps(b, indent = 2))
            #print("%s %s"%(b["battleTime"], b["type"]))

            # opponent -> crowns (compare???), team [0] crowns???

            # safety check in case Supercell sent stale data, or we loaded clan members from saved state, and someone
            # new joined:
            if playerTag not in playerTag:
                playerTag[playerTag] = PlayerStats()


            if battleType=="riverRaceDuel" or battleType == "riverRaceDuelColosseum": 
                defenderCrown = b["team"][0]["crowns"]
                opponentCrown = b["opponent"][0]["crowns"]
                # print("%s %s by %s  %s:%s"%(b["battleTime"], b["type"], cr.getPlayerName(playerTag),defenderCrown, opponentCrown))
                # print("Team Card length:%s" % len(b["team"][0]["cards"]))

                # extra validation (people can move clans, and we want only our wars to be considered!)
                if b["team"][0]["clan"]["tag"][1:] != ct:
                    continue # this is not for our clan!

                gameCount = len(b["team"][0]["cards"]) / 8
                if(defenderCrown>opponentCrown): # won the duel
                   player[playerTag].battlesWon += gameCount
                player[playerTag].battlesPlayed += gameCount
                player[playerTag].name = b["team"][0]["name"]
                
                
            elif battleType=="riverRacePvP":
                # extra validation (people can move clans, and we want only our wars to be considered!)
                if b["team"][0]["clan"]["tag"][1:] != ct:
                    continue # this is not for our clan!

                defenderCrown = b["team"][0]["crowns"]
                opponentCrown = b["opponent"][0]["crowns"]
                if(defenderCrown>opponentCrown): # won the battle
                    player[playerTag].battlesWon += 1
                player[playerTag].battlesPlayed += 1 
                player[playerTag].name = b["team"][0]["name"]

            else: # boatBattle
                player[playerTag].battlesPlayed += 1
                player[playerTag].boatAttacks += 1
                # TODO: can I get the name here?!!


# Iterate through clan members, collect clan level stats, incomplete games, player stats
# results are saved, and information gathering is resumed if the call is run again
def getPlayerStats(ct, warStartTime, o):

    # Check if there is already a saved state available
    # TODO: control via option
    # TODO: log!
    if o.freshData:
        ts, ps = warStartTime, dict()
    else:
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
        populateWarGames(m, ts, ps, ct, o)

    # serialize the data and save
    if not o.readOnly:
        cri.saveGameState(ct, warStartTime, dataCollectedAt, ps)

    return ps


# Print clan's statistics for the war day (participant numbers, win ratio)
def printClanWarDayStats(ct, playerStats):
    cd = ClanData()
    clanName = cr.getClanName(ct)
    participants = 0
    for key, value in playerStats.items():
        cd.battlesWon += value.battlesWon
        cd.battlesPlayed += value.battlesPlayed
        if value.battlesPlayed > 0:
            participants += 1

    if cd.battlesPlayed == 0:
        winRatio = 0
    else:        
        winRatio = round(100*cd.battlesWon/cd.battlesPlayed,2)

    print("%s: %s war battles played, %s won (%s%% win rate), %s members participated"%
        (clanName,cd.battlesPlayed, cd.battlesWon, winRatio, participants))

# Print the players and the number of war games completed during the active war two day
def printWhoHasIncompleteGames(ct, playerStats):
    for key, value in sorted(playerStats.items(), reverse=True, key=lambda item: item[1].battlesPlayed):
        if value.limitedInfo:
            caveatMsg = "25+ games since war start"
        else:
            caveatMsg = ""

        if value.name == "":
            playerName = cr.getPlayerName(key)
        else:
            playerName = value.name
        print("%s: %s %s" % (playerName,int(value.battlesPlayed), caveatMsg))




def printUsageInformation():
    print("""
        This script will help with managing your Clash Royale Clan War 2 participation.
        Use the following arguments:
            battles
                Prints every clan member in the clan, and the number of war day battles completed. Note
                that only limited battle information is available from Supercel. This script queries 
                Supercel, saves the results, and subsequent calls to the script will incrementally
                update the data, so regular use will improve data accuracy.
                The clan members are printed in reverse order of number of war day battles played.
            clan
                Privides war day statistics for your clan
            clans
                Identifies all the river race clans for your clan, runs a war day statistics on them, and 
                indicates participation and win ratio for the last war day. Limited game result is available 
                from Supercel, but if you run this regularly the information from Supercel is persisted, 
                and the accuracy of the information will be better.
        """)


# for development, eventually will get to something that will debug a single player
def tmp_debug():
    warStartTime = getWarStartPrefix()
    ts, ps = warStartTime, dict()
    playerTag = cr.myClanTag
    
    o = CROptions()
    o.debugBattles = True
    ps[playerTag] = PlayerStats()

    populateWarGames(playerTag, warStartTime, ps, cr.myClanTag, o)



def main(argv):

    o = CROptions()

    # for debugging:
    # o.freshData = True
    # o.readOnly = True

    if len (argv) == 0:
        printUsageInformation()
        exit()
    cmd = argv[0]
    if cmd == "battles":
        warStartTime = getWarStartPrefix()
        pss = getPlayerStats(cr.myClanTag, warStartTime, o)
        printWhoHasIncompleteGames(cr.myClanTag, pss)
    elif cmd == "clan":
        warStartTime = getWarStartPrefix()
        pss = getPlayerStats(cr.myClanTag, warStartTime, o)
        printClanWarDayStats(cr.myClanTag, pss)
    elif cmd == "clans":
        warStartTime = getWarStartPrefix()
        clanTags = cr.getRiverRaceClanList(cr.myClanTag)
        for ct in clanTags:
            pss = getPlayerStats(ct, warStartTime, o)
            printClanWarDayStats(ct, pss)
    elif cmd == "debug1":
        tmp_debug()
    else:
        printUsageInformation()

if __name__ == "__main__":
    main(sys.argv[1:])
