# Utility Functions to query individual battles

import sys
import json
import CRLib as cr

def battleTime(b):
    try:
        return b["battleTime"]
    except:
        print("Battle time could not be determined for this battle.", file=sys.stderr)
        print (json.dumps(b, indent = 2), file=sys.stderr)
        return ""


def battleType(b):
    try:
        return b["type"]
    except:
        print("Battle type could not be determined for this battle.", file=sys.stderr)
        print (json.dumps(b, indent = 2), file=sys.stderr)
        return ""


def playerName(b):
    try:
        return b["team"][0]["name"]
    except:
        print("Battle player name could not be determined for this battle.", file=sys.stderr)
        return ""

def playerTag(b):
    try:
        return b["team"][0]["tag"][1::]
    except:
        print("Battle player tag could not be determined for this battle.", file=sys.stderr)
        return ""


def battleClanTag(b):
    try:
        return b["team"][0]["clan"]["tag"][1:]
    except:
        print("Battle clan tag could not be determined for this battle.", file=sys.stderr)
        return ""

# For PvP games
def PvPWon(b):
    defenderCrown = b["team"][0]["crowns"]
    opponentCrown = b["opponent"][0]["crowns"]
    if(defenderCrown>opponentCrown): # won the battle
        return True
    else:
        return False

# For duels get the 
def isDuel(b):
    try:
        bt = battleType(b)
        if bt=="riverRaceDuel" or bt == "riverRaceDuelColosseum":
            return True
    except:
        print("Battle duel type could not be determined for this battle.", file=sys.stderr)
        return False


def duelWon(b):
    def get_towers_count(t):
        return (1 if "kingTowerHitPoints" in t and t["kingTowerHitPoints"] else 0) + \
            (len(t["princessTowersHitPoints"]) if "princessTowersHitPoints" in t else 0)

    player_towers = get_towers_count(b["team"][0])
    opponent_towers = get_towers_count(b["opponent"][0])
    return player_towers > opponent_towers  # won the duel if true


def duelGameCount(b):
    try:
        return int(len(b["team"][0]["cards"]) / 8)
    except:
        return 0


def csvBattleMessage(b):
    csvLine = f'{battleClanTag(b)},{cr.reformatCRTimestamp(battleTime(b))},'\
              f'{playerName(b)},{battleType(b)},'
    if isDuel(b):
        csvLine += f'{duelGameCount(b)},{duelWon(b)}'
    else:
        csvLine += f'1,{PvPWon(b)}'
    return csvLine

        

def duelDefenderCrowns(b):
    try:
        return b["team"][0]["crowns"]
    except:
        print("Battle Duel: could not determine defender crowns.", file=sys.stderr)
        return 0


def duelOpponentCrowns(b):
    try:
        return b["opponent"][0]["crowns"]
    except:
        print("Battle Duel: could not determine opponent crowns.", file=sys.stderr)
        return 0


def duelBattlesWon(b):
    try:
        defenderCrown = duelDefenderCrowns(b)
        opponentCrown = duelOpponentCrowns(b)

        if duelGameCount(b) == 2:
            if(defenderCrown>opponentCrown): # won the duel
                return 2
            else:
                # 3 games, 1:2 - look at the tower damage in the last one!
                if duelWon(b):
                    return 2
                else:
                    return 1
    except:
        return 0
    return 0
