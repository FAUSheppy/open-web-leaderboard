# Open Web Leaderboard
The Open Web Leaderboard is a leaderboard that can easily be used with any backend as long as you find a way to supply the following information (see database.py):
    
- getRankRange(start, end) -> return a list of players from start rank to end rank
- getMaxEntries() -> return the total number of entries in the leaderboard
- findPlayer() -> find a player by name and return a (player, rank)-tupel

The system was developed to be used with the [skillbird-framwork](https://github.com/FAUSheppy/skillbird). If you use this framework, the program should be working without any arguments. If you need more conductibility feel free to open a pull-request or send me a message.

# How to run
You can run the leaderboard as a flask standalone (arguments overwrite *config.py* settings!):

    ./server.py --skillbird-db PATH_TO_DB

or with a runner like *waitress*:

    /usr/bin/waitress-serve --host 127.0.0.1 --port 5002 --call 'app:createApp

the *DB_PATH* is set in *config.py* in this case.

# Preview
![open-web-leaderboard](https://media.atlantishq.de/leaderboard-github-picture.png)

# Live Demo
[insurgency.atlantishq.de](https://insurgency.atlantishq.de)
