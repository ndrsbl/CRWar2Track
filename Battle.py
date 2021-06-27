# Utility Functions to query individual battles

import sys

def battleTime(b):
    try:
        return b["battleTime"]
    except:
        print("Battle time could not be determined for this battle.", file=sys.stderr)
        return ""


def battleType(b):
    try:
        return b["type"]
    except:
        print("Battle type could not be determined for this battle.", file=sys.stderr)
        return ""

def battleClanTag(b):
    try:
        b["team"][0]["clan"]["tag"][1:]
    except:
        print("Battle clan tag could not be determined for this battle.", file=sys.stderr)
        return ""

    