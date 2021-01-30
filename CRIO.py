import pickle
import glob
import os


# Saves the GameState at a particular timestamp
def saveGameState(clantTag, warStart, ts, d):
    if not os.path.exists('./data/'):
        os.makedirs('./data')
    with open("./data/" + clantTag + "-" + warStart+"-"+ts+".pic", 'wb') as file:
        pickle.dump(ts, file) # Timestamp of the dataset
        pickle.dump(d, file) # The gathered war data

# Retrieves saved game state for a clan, for a particular war day. Includes the timestamp of the
# dataset
def loadGameState(clantTag, warStart):
    prefix = "./data/" + clantTag + "-" + warStart 
    files = glob.glob(prefix + "*.pic")
    if len(files) > 0:
        latestFile = max(files) # timestamp ordering is good for us

        with open(latestFile, 'rb') as file:
            ts = pickle.load(file)
            dd = pickle.load(file)
            return (ts, dd)
    return None