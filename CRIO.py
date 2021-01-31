import pickle
import glob
import os
import itertools


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



# Generate a grouping key for a filename to identify one data file per day per clan
# The filename format is clan-warday-timestamp
def genKey(fileName):
    parts = fileName.split('-')
    if len(parts) < 3:
        return None # junk data?
    prefix = f"{parts[0]}-{parts[1]}"
    return prefix


# cleans up historical data files, keeps the latest for each day
def purgeGameState():
    if not os.path.exists('./data/'):
        return
    prefix = "./data/"
    files = glob.glob(prefix + "*.pic")
    files.sort()
    for k,v in itertools.groupby(files, key = genKey):
        filesToDelete = list(v)
        filesToDelete.sort()
        filesToDelete = filesToDelete[:-1]
        for f in filesToDelete:
            try:
                os.remove(f)
            except OSError as e:
                print(f"Error: Cannot delete {f}, {e.strerror}")

