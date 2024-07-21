# Open Web Leaderboard
The Open Web Leaderboard is a leaderboard that can easily be used with any backend as long as you find a way to supply the following information (see database.py):
    
- getRankRange(start, end) -> return a list of players from start rank to end rank
- getMaxEntries() -> return the total number of entries in the leaderboard
- findPlayer() -> find a player by name and return a (player, rank)-tupel

The system was developed to be used with the [skillbird-framwork](https://github.com/FAUSheppy/skillbird). If you use this framework, the program should be working without any arguments. If you need more conductibility feel free to open a pull-request or send me a message.

# Requirements
- [MDB Jquery](https://mdbootstrap.com/docs/jquery/getting-started/download/) (unpack to ./static/bootstrap/)
- [Fontawesome](https://fontawesome.com/download) (move to static/boostrap/fontawesome.css)
- ``python3 -m pip install -r req.txt``
- [Moment.js](https://momentjs.com/downloads/moment.js) (directly into static/)


# How to run
You can run the leaderboard as a flask standalone (arguments overwrite *config.py* settings!):

    ./server.py --skillbird-db PATH_TO_DB

or with a runner like *waitress*:

    /usr/bin/waitress-serve --host 127.0.0.1 --port 5002 --call 'app:createApp'

the *DB_PATH* is set in *config.py* in this case.

# GDPR: Blacklisting players
Players can be blacklisted by name via a *blacklist.json* file in the project root.

    {
        "blacklist" : ["name", "name_2"]
    }

# Adding servers for player count live info
**THIS FEATURE IS DISABLED BECAUSE py-valve DOES NOT SUPPORT PYTHON>3.9**
Source-Servers can be added via the *servers.json*-file:

    [
        {
            "name" : "server_1",
            "host" : "example.com",
            "port" : 27015
        },
        {
            ...
        }
    ]
    
*Python-valve* is required if this file exists.

# Live Demo
[insurgency.atlantishq.de](https://insurgency.atlantishq.de)
