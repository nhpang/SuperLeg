def getTodaysGames():
    from nba_api.live.nba.endpoints import scoreboard
 
    # Today's Score Board
    games = scoreboard.ScoreBoard()

    # json
    games = games.get_dict()

    from datetime import datetime

    games_list = []

    for i in games['scoreboard']['games']:
        # print(i)

        game = {}

        game.update({'Title': i['homeTeam']['teamName']+ ' vs ' +i['awayTeam']['teamName']})
        game.update({'GameID': i['gameId']})

        games_list.append(game)
 
    return games_list

fortnite = getTodaysGames()

for gameId in fortnite:

    from nba_api.stats.endpoints import boxscoretraditionalv3

    games = boxscoretraditionalv3.BoxScoreTraditionalV3('0022400968')

        # json
    games = games.get_data_frames()[0]
    print(games)