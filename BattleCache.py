# Battle Cache

from datetime import datetime, timedelta
import requests
import json
import itertools
import CRLib as cr
import CRIO as cri
import sys
import argparse
import pickle
import glob
import os



# Dict of dicts: for every player store a dict of battles indexed by timestamp
class Battles:
    def __init__(self):
        self.d = dict() # all player dictionaries 


    # Add clan war related battles for a player
    def populateWarBattles(self, playerTag):
        r2=requests.get("https://api.clashroyale.com/v1/players/%23"+playerTag+"/battlelog", 
        headers = {"Accept":"application/json", "authorization":cr.auth}, 
        params = {"limit":100})
        battles = r2.json()

        if len(battles) == 0:
            return
        
        if playerTag not in self.d:
            self.d[playerTag] = dict()
        playerGameStore = self.d[playerTag]

        for b in battles:
            battleType = b["type"]
            if((battleType=="riverRaceDuel"  
                or battleType=="riverRaceDuelColosseum"  
                or battleType=="riverRacePvP" 
                or battleType=="boatBattle")):

                ts = b["battleTime"]
                if ts not in playerGameStore:
                    playerGameStore[ts] = b

    # A list of battles for a player
    def getBattlesForPlayer(self, pt):
        if pt not in self.d:
            return []
        else:
            return list(self.d[pt].items())

    # A list of battles for a player
    # Samle timestamp: 20210510T143914.000Z - string, lexicographical comparison
    def getBattlesForPlayer(self, pt, startTime, endTime):
        if pt not in self.d:
            return []
        else:
            ret = []
            for t, b in self.d[pt].items():
                if (b["battleTime"] >= startTime) and (b["battleTime"] < endTime):
                    ret.append(b)
            return ret


    # Load from disk the battles of a single player
    def loadState(self, pt):
        filename = "./data/" + pt + ".pic"
        if os.path.exists('./data/') and os.path.exists(filename):
            with open(filename, 'rb') as file:
                dd = pickle.load(file)
                return dd
        return None

    # Saves the GameState at a particular player
    # pt: playertag
    def saveState(self, pt, d):
        if not os.path.exists('./data/'):
            os.makedirs('./data')
        with open("./data/" + pt + ".pic", 'wb') as file:
            pickle.dump(d, file) 

    ## TODO: purge the history for a player
    def purgeState(self, ps):
        pass
