# CRWar2Track
Scripts to track Clas Royale's war 2 clan participation

The purpose of these scripts are to help manage an active war clan in Clash Royale.
It shows participation during the last 24 hours, which we use to chase people to complete
their war day battles. 


To use:
First of all get an access token from Supercel:
* Register on developer.clashroyale.com/
* Create an `auth.txt` file with the authorization token inside.



Add your favourite clan to get stats for in CRLib.py. An example is 
`clanTagHW = "YJCGRV9" # Heavyweights`
You can then refer to this in the main script.

Modify CW2DayAnalysis.py to use this new clan tag instead of the one above.

Run CW2DayAnalysis.py


This will determine the start of the war day. On Mondays it is the last 9:30am GMT,
on other days it is the last 10:00am GMT. The script will go through all the current clan 
members, and list the number of war day battles they played. E.g.
```
player1: 4
player2: 4
player3: 3
playern: 0
```

Note that only the last 25 games are available per player, so war day information may not be
available. The script will give a warning in such cases for the player:

```
playerFoo: 2 25+ games since war start
```


