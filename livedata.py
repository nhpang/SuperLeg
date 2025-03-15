def getLiveUpcomingGames():
    from nba_api.live.nba.endpoints import scoreboard

    # Today's Score Board
    games = scoreboard.ScoreBoard()

    # json
    games = games.get_dict()

    from datetime import datetime

    games_list = []

    for i in games['scoreboard']['games']:
        print(i)

        game = {}

        # get each team score by adding each periods points
        home_score = 0
        for quarter in i['homeTeam']['periods']:
            home_score += quarter['score']
        away_score = 0
        for quarter in i['awayTeam']['periods']:
            away_score += quarter['score']

        gamescore = i['homeTeam']['teamName'] + ' ' + str(home_score) +' - ' + i['awayTeam']['teamName'] + ' ' + str(away_score)

        game.update({'Game Score': gamescore})
        game.update({'Status': i['gameStatusText']})
        game.update({'Start Time': i['gameTimeUTC']})

        games_list.append(game)

    # sort my start time
    games_list.sort(key=lambda x: datetime.fromisoformat(x['Start Time']))

    return games_list


getLiveUpcomingGames()