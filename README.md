# Open Web Leaderboard
The Open Web Leaderboard is a leaderboard that can easily be used with any backend as long as you find a way to supply the following information:
    
- getRankRange(start, end) -> return a list of players from start rank to end rank
- getMaxEntries() -> return the total number of entries in the leaderboard
- findPlayer() -> find a player by name

The system was developed to be used with the [skillbird-framwork](https://github.com/FAUSheppy/skillbird). If you use this framework, the program should be working without any arguments. If you need more conductibility feel free to open a pull-request or send me a message.

# Preview
![open-web-leaderboard](https://media.atlantishq.de/leaderboard-github-picture.png)

# Live Demo
[rating.atlantishq.de](https://rating.atlantishq.de)
