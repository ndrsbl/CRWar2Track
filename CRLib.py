# Common utilas for accessing Clash Royale API
import requests
import json
import itertools


myClanTag = "YJCGRV9" # Heavyweights
myPlayerTag = "8YPRYCC8R" # drKot 

def loadAuth():
    try:
        with open("auth.txt", "r") as f:
            rv = "Bearer " + f.read().rstrip()
            return rv
    except IOError:
        sys.exit("Could not read authentication token, make sure one is available in an auth.txt file.")
auth = loadAuth()

def getClanName(clanTag):
    d=dict()
    r=requests.get("https://api.clashroyale.com/v1/clans/%23"+clanTag, 
    headers = {"Accept":"application/json", "authorization":auth}, 
    params = {"limit":50,"clanTag":clanTag})
    return r.json()["name"]


def getPlayerName(playerTag):
    d=dict()
    r=requests.get("https://api.clashroyale.com/v1/players/%23"+playerTag, 
    headers = {"Accept":"application/json", "authorization":auth}, 
    params = {"limit":50,"playerTag":playerTag})
    return r.json()["name"]

def clanMemberTags(ct):
    tags = []
    r=requests.get("https://api.clashroyale.com/v1/clans/%23"+ct+"/members", 
    headers = {"Accept":"application/json", "authorization":auth}, 
    params = {"limit":50})

    members = r.json()["items"]
    for m in members:
        tags.append(m["tag"][1:])
    return tags   


# Given a clan tag return the clan tags in the current river race
def getRiverRaceClanList(ct):
    r2=requests.get("https://api.clashroyale.com/v1/clans/%23"+ct+"/currentriverrace", 
    headers = {"Accept":"application/json", "authorization":auth}, 
    params = {"limit":10})
    clans = r2.json()["clans"]
    rv = []
    for c in clans:
        rv.append(c["tag"][1:])
    return rv
    