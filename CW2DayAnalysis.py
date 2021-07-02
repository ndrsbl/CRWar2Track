# War 2 analysis: going through partner clans and for all check
# last 25 battles, how many are war, and show win ratio, etc.

from datetime import datetime, timedelta
import requests
import json
import itertools
import CRLib as cr
import CRIO as cri
import sys
import argparse
import Battle
import BattleCache


class CROptions:
    def __init__(self):
        self.freshData = False # Do not read saved state from the data directory
        self.readOnly = False # Persist battles into the data directory
        self.historical = False # Only load historical data, and do not gather this from Supercel
        self.debugBattles = False # Internal, debug battles (CR keeps changing things for the war!)
        self.includeOutOfClan = False # Include players who are no longer in the clan (for rotation tracking)

class ClanData:
    def __init__(self):
        self.battlesWon = 0
        self.battlesPlayed = 0
        self.boatAttacks = 0


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
    today = today - timedelta(hours=9, minutes=50)
    #today = today - timedelta(hours=10, minutes=55)

    timestamp = today.strftime("%Y%m%d")
    if today.isoweekday == 1: # Monday, start of river race -> we look at 9:30
        timestamp += "T0951"
    else:
        timestamp += "T0951"
    return timestamp

# For a list of battles gather war day statistics. 
# Battles are already expected to be specific to a particular war day and clan
def getWarDayStatsForBattles(battles, o):
    #if o.debugBattles:
        #print(f'b["battleTime"] b["team"][0]["name"] b["type"]')
        #print(json.dumps(b, indent = 2))
    playerStats = dict()

    for b in battles:
        battleType = Battle.battleType(b)
        battleTime = Battle.battleTime(b)
        playerTag = Battle.playerTag(b)
        if(battleType=="riverRaceDuel"  
            or battleType=="riverRaceDuelColosseum"  
            or battleType=="riverRacePvP" 
            or battleType=="boatBattle") :

            # safety check in case Supercell sent stale data, or we loaded clan members from saved state, and someone
            # new joined:
            if playerTag not in playerStats:
                playerStats[playerTag] = PlayerStats()

            if Battle.isDuel(b): 
                defenderCrown = Battle.duelDefenderCrowns(b)
                opponentCrown = Battle.duelOpponentCrowns(b)

                gameCount = Battle.duelGameCount(b)

                if o.debugBattles:
                    print(Battle.csvBattleMessage(b))
                    # print(f'DEBUG: {Battle.battleClanTag(b)} {cr.reformatCRTimestamp(battleTime)} '\
                    #     f'{cr.getPlayerName(playerTag)} duel {defenderCrown}:{opponentCrown} [{gameCount}]')

                playerStats[playerTag].battlesWon += Battle.duelBattlesWon(b)
                    
                playerStats[playerTag].battlesPlayed += gameCount
                playerStats[playerTag].name = b["team"][0]["name"]
                
                
            elif battleType=="riverRacePvP":
                if o.debugBattles:
                    print(Battle.csvBattleMessage(b))
                    # print(f'DEBUG: {Battle.battleClanTag(b)} {cr.reformatCRTimestamp(battleTime)}'\
                    #     f' {cr.getPlayerName(playerTag)} 1v1')

                if Battle.PvPWon(b):
                    playerStats[playerTag].battlesWon += 1
                playerStats[playerTag].battlesPlayed += 1 
                playerStats[playerTag].name = b["team"][0]["name"]

            else: # boatBattle
                if b["boatBattleSide"] == "attacker":
                    if o.debugBattles:
                        print(f'DEBUG: {Battle.battleClanTag(b)} {cr.reformatCRTimestamp(battleTime)}'\
                        f' {cr.getPlayerName(playerTag)} boat attack')

                    playerStats[playerTag].battlesPlayed += 1
                    playerStats[playerTag].boatAttacks += 1
                else:
                    # Our boat got attacked:
                    if o.debugBattles:
                        print(f'DEBUG: {Battle.battleClanTag(b)} {cr.reformatCRTimestamp(battleTime)}'\
                        f' {cr.getPlayerName(playerTag)} won={b["boatBattleWon"]}'\
                        f' new_towers_destroyed={b["newTowersDestroyed"]} boat attacked by {b["opponent"][0]["clan"]["name"]}')
    return playerStats


# Print clan's statistics for the war day (participant numbers, win ratio)
def printClanWarDayStats(ct, playerStats):
    cd = ClanData()
    clanName = cr.getClanName(ct)
    participants = 0
    boatattacks = 0
    for key, value in playerStats.items():
        cd.battlesWon += value.battlesWon
        cd.battlesPlayed += value.battlesPlayed
        cd.boatAttacks += value.boatAttacks
        if value.battlesPlayed > 0:
            participants += 1
        
    battlesPlayed = cd.battlesPlayed - cd.boatAttacks
    if battlesPlayed == 0:
        winRatio = 0
    else:        
        winRatio = round(100*cd.battlesWon/battlesPlayed,2)

    print(f"{clanName}: {cd.battlesPlayed} war battles, {cd.battlesWon} " +
        f"won ({winRatio}% win rate excl boat), {cd.boatAttacks} boat attacks, {participants} participated")

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
        print(f"{playerName}:{int(value.battlesWon)}/{int(value.battlesPlayed)} {caveatMsg}")




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



def main(args):
    o = CROptions()
    if args.readonly:
        o.freshData = True
        o.readOnly = True
    if args.freshdata:
        o.freshData = True
    if args.nosave:        
        o.readOnly = True
    if args.historical:        
        o.historical = True        
        o.readOnly = True
    if args.verbose:
        o.debugBattles = True


    if len (args.command) == 0:
        printUsageInformation()
        exit()
    cmd = args.command[0]

    clanTag = cr.myClanTag

    warStartTime = getWarStartPrefix()  
    bc = BattleCache.Battles()

    if cmd == "battles":
        bc.polulateWarBattlesForRiverRace(clanTag, o.freshData, o.historical, o.readOnly)
        battles = bc.getBattlesForRiverRace(clanTag, warStartTime, None)
        ps = getWarDayStatsForBattles(battles, o)
        print(ps)
        printWhoHasIncompleteGames(clanTag, ps)
    elif cmd == "clan":
        bc.polulateWarBattlesForRiverRace(clanTag, o.freshData, o.historical, o.readOnly)
        battles = bc.getBattlesForRiverRace(clanTag, warStartTime, None)
        ps = getWarDayStatsForBattles(battles, o)
        printClanWarDayStats(clanTag, ps)
    elif cmd == "clans":
        clanTags = cr.getRiverRaceClanList(clanTag)
        for ct in clanTags:
            bc.polulateWarBattlesForRiverRace(ct, o.freshData, o.historical, o.readOnly)
            battles = bc.getBattlesForRiverRace(ct, warStartTime, None)
            ps = getWarDayStatsForBattles(battles, o)
            printClanWarDayStats(ct, ps)
    elif cmd == "purge":
        # purge old historical files, but keep one per war day
        cri.purgeGameState()
    else:
        printUsageInformation()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs=1, choices=['battles', 'clan', 'clans', 'purge'],
                        help='command indicating the type of war analytics to return')
    parser.add_argument('-r', '--readonly', action="store_true")
    parser.add_argument('-f', '--freshdata', action="store_true")
    parser.add_argument('-n', '--nosave', action="store_true")
    parser.add_argument('-i', '--historical', action="store_true")
        #help='Only load saved data, do no query supercell for war log')
    parser.add_argument('-v', '--verbose', action="store_true")

    args = parser.parse_args()
    main(args)

