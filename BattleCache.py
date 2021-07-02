# Battle Cache

from datetime import datetime, timedelta
import requests
import CRLib as cr
import CRIO as cri
import pickle
import glob
import os
import Battle



# Dict of dicts: for every player store a dict of battles indexed by timestamp
class Battles:
    def __init__(self):
        self.d = dict() # all player dictionaries 


    # Add clan war related battles for a player
    def populateWarBattlesForPlayer(self, playerTag):
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

    def polulateWarBattlesForClan(self, ct):
        for m in cr.clanMemberTags(ct): 
            self.populateWarBattlesForPlayer(m)

    def polulateWarBattlesForRiverRace(self, ct, skipOld, skipOnline, skipSave):
        ret = []
        if skipOld == False:
            self.loadState()
        if skipOnline == False:
            for m in cr.clanMemberInRiverRace(ct): 
                self.populateWarBattlesForPlayer(m)
            if skipSave == False: # Only makes sense to save if we loaded something online
                self.saveState()
        return ret

    # A list of battles for a player
    def getBattlesForPlayer(self, pt):
        if pt not in self.d:
            return []
        else:
            return list(self.d[pt].items())

    # A list of battles for a player
    # Samle timestamp: 20210510T143914.000Z - string, lexicographical comparison
    def getBattlesForPlayer(self, pt, ct, startTime, endTime):
        if endTime is None:
            endTime = '20990101T010101.000Z'
        if pt not in self.d:
            return []
        else:
            ret = []
            for t, b in self.d[pt].items():
                if (b["battleTime"] >= startTime) and (b["battleTime"] < endTime):
                    if ct is None:
                        ret.append(b)
                    else:
                        if Battle.battleClanTag(b) == ct:
                            ret.append(b)
            return ret


    def getBattlesForClan(self, ct, startTime, endTime):
        ret = []
        for pt in cr.clanMemberTags(ct):
            ret = ret + self.getBattlesForPlayer(pt, ct, startTime, endTime)
        return ret

    def getBattlesForRiverRace(self, ct, startTime, endTime):
        ret = []
        for pt in cr.clanMemberInRiverRace(ct):
            ret = ret + self.getBattlesForPlayer(pt, ct, startTime, endTime)
        return ret

    # Load from disk the battles of a single player
    def loadStatePlayer(self, filename, pt):
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                dd = pickle.load(file)
                return dd
        return None

    # Saves the GameState at a particular player
    # pt: playertag
    def saveStatePlayer(self, pt, d):
        if not os.path.exists('./data/'):
            os.makedirs('./data')
        with open("./data/" + pt + ".pic2", 'wb') as file:
            pickle.dump(d, file) 

    def saveState(self):
        for k,v in self.d.items():
            self.saveStatePlayer(k, v)

    def loadState(self):
        paths = glob.glob('./data/*.pic2')
        for path in paths:
            basename = os.path.basename(path)
            pt = os.path.splitext(basename)[0]
            dd = self.loadStatePlayer(path, pt)
            if len(dd) > 0:
                self.d[pt] = dd

    ## TODO: purge the history for a player
    def purgeState(self, ps):
        pass
