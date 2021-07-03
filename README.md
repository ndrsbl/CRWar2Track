# CRWar2Track
Scripts to track Clash Royale's war 2 clan participation

The purpose of these scripts are to help manage an active war clan in Clash Royale.
It shows participation during the last 24 hours, which we use to chase people to complete
their war day battles. 


To use:
First of all get an access token from Supercel:
* Register on developer.clashroyale.com/
* Create an `auth.txt` file with the authorization token inside.



Add your favourite clan to get stats for in CRLib.py. An example is 
`myClanTag = "YJCGRV9" # Heavyweights`
`myPlayerTag = "8YPRYCC8R" # drKot`
You can then refer to this in the main script.

The main script is `W2DayAnalysis.py`
It takes multiple commands: battles, clan, clans. 


        battles
            Prints every clan member in the clan, and the number of war day battles completed. Note
            that only limited battle information is available from Supercel. T
            The clan members are printed in reverse order of number of war day battles played.
            The output will be similar to:
            ```
            player1: 4
            player2: 4
            player3: 3
            playern: 0
            ```
            Where the numbers are the number of battles played in the last active war day 
        clan
            Privides war day statistics for your clan
            An example output will be like:
            ```
            Heavyweights: 80.0 war battles played, 48.0 won (60.0% win rate), 23 members participated
            ```

        clans
            Identifies all the river race clans for your clan, runs a war day statistics on them, and 
            indicates participation and win ratio for the last war day. Limited game result is available 
            from Supercel, but if you run this regularly the information from Supercel is persisted, 
            and the accuracy of the information will be better. An example output:
            
                Heavyweights: 188 war battles, 108 won (57.45% win rate excl boat), 0 boat attacks, 47 participated
                B****: 200 war battles, 138 won (69.0% win rate excl boat), 0 boat attacks, 50 participated
                D****: 191 war battles, 89 won (46.6% win rate excl boat), 0 boat attacks, 49 participated
                i***s: 180 war battles, 74 won (41.11% win rate excl boat), 0 boat attacks, 46 participated
                V****: 187 war battles, 75 won (40.11% win rate excl boat), 0 boat attacks, 48 participated



The script will determine the start of the war day. On Mondays it is the last 9:30am GMT,
on other days it is the last 10:00am GMT. 

Note that only the last 25 games are available per player, so war day information may not be
available unless you run the script frequently enough to gather full game coverage.

At the time when this script queries Supercel it saves the results, and subsequent calls to the script 
will incrementally update the data, so regular use will improve data accuracy. The persisted data is 
stored in data directory. Accessing historical data, and overriding war times, as well as read only mode
is coming.


