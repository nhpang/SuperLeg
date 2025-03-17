from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from bs4 import BeautifulSoup
import requests
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


app = Flask(__name__)
CORS(app)

@app.route('/stats', methods=['POST'])
def stats():
    data = request.json
    name = data['name']

    print('Gathering player games and information...')
    game, img, player, accolades = games(name)

    print('Calculating player averages...')
    average=averages(game)

    print('Predicting next statline...')
    predict=prediction(game)

    game, img, player, accolades = games(name)

    return jsonify({
        'game': game.to_csv(),
        'average': average,
        'prediction': predict,
        'image': f'{img}',
        'player': f'{player}',
        'accolades': f'{accolades}'
    })

@app.route('/search', methods=['GET'])
def search():
    from nba_api.stats.endpoints import commonallplayers
    # get all players
    players = commonallplayers.CommonAllPlayers().get_data_frames()[0]
    # only active
    current_players = players[players["ROSTERSTATUS"] > 0]
    # put names into list
    names=[]
    for i in current_players['DISPLAY_FIRST_LAST']:
        names.append(i)
    # return names
    return(names)

@app.route('/today', methods=['GET'])
def getTodaysGames():
    from nba_api.live.nba.endpoints import scoreboard
    from datetime import datetime, timedelta
 
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

        if i['homeTeam']['teamTricode'] == 'UTA':
            awaytri = 'utah'
        elif i['homeTeam']['teamTricode'] == 'NOP':
            awaytri = 'no'
        else:
            awaytri = i['homeTeam']['teamTricode']

        if i['awayTeam']['teamTricode'] == 'UTA':
            hometri = 'utah'
        elif i['awayTeam']['teamTricode'] == 'NOP':
            hometri = 'no'
        else:
            hometri = i['awayTeam']['teamTricode']

        if (i['gameStatusText'])[-2:] == 'ET':
            status = "Starting Soon..."
        else:
            status = i['gameStatusText']

        time = i['gameEt']
        time = datetime.strptime(time,'%Y-%m-%dT%H:%M:%SZ')
        time = str(time - timedelta(hours=3))
        time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        time = time.strftime("%a, %d %b %Y %I:%M %p")
        print((time))

        game.update({'Title': i['homeTeam']['teamName']+ ' vs ' +i['awayTeam']['teamName']})
        game.update({'Game Score': str(home_score) + ' - ' + str(away_score)})
        game.update({'Status': i['gameStatusText']})
        game.update({'Start Time': str(time)})
        game.update({'GameID': i['gameId']})
        game.update({'hometeamTricode': hometri})
        game.update({'awayteamTricode': awaytri})

        games_list.append(game)
 
    return games_list

@app.route('/past', methods=['GET'])
def getPastGames():
    
    from nba_api.stats.endpoints import scheduleleaguev2
    from datetime import datetime, timedelta
    games = scheduleleaguev2.ScheduleLeagueV2()

    df = games.get_data_frames()[0]

    # good format
    df['gameDateTimeEst'] = pd.to_datetime(df['gameDateTimeEst'], format='%Y-%m-%dT%H:%M:%SZ')
    print(df['gameDateTimeEst'])
    # timezone to van
    df['gameDateTimeEst'] = df['gameDateTimeEst'] - timedelta(hours=3)
    # get get request date
    current_datetime = datetime.strptime(request.args['date'][:-1], "%Y-%m-%d %H:%M:%S")
    print(current_datetime)
    # get the day before that request day
    yesterday = current_datetime - pd.Timedelta(days=1)
    # limit df to that request day
    df = df[df['gameDateTimeEst'].dt.date == yesterday.date()]
    # limit columns to relevant
    df =df.loc[:, ['gameDateTimeEst', 'gameId', 'homeTeam_teamName', 'homeTeam_score', 'awayTeam_teamName', 'awayTeam_score', 'gameStatusText', 'homeTeam_teamTricode', 'awayTeam_teamTricode']]
    # sort entries by date
    df = df.sort_values(by='gameDateTimeEst')

    games_list = []

    for row in df.iterrows():
        game = {}

        if row[1]['homeTeam_teamTricode'] == 'UTA':
            awaytri = 'utah'
        elif row[1]['homeTeam_teamTricode'] == 'NOP':
            awaytri = 'no'
        else:
            awaytri = row[1]['homeTeam_teamTricode']

        if row[1]['awayTeam_teamTricode'] == 'UTA':
            hometri = 'utah'
        elif row[1]['awayTeam_teamTricode'] == 'NOP':
            hometri = 'no'
        else:
            hometri = row[1]['awayTeam_teamTricode']

        game.update({'Title': row[1]['homeTeam_teamName'] + ' vs ' + row[1]['awayTeam_teamName']})
        game.update({'Game Score': str(row[1]['homeTeam_score']) +' - ' + str(row[1]['awayTeam_score'])})
        game.update({'Status': row[1]['gameStatusText']})
        game.update({'Start Time': str((row[1]['gameDateTimeEst'].strftime("%a, %d %b %Y %I:%M %p")))})
        game.update({'GameID': row[1]['gameId']})
        game.update({'hometeamTricode': hometri})
        game.update({'awayteamTricode': awaytri})

        games_list.append(game)

    return games_list

@app.route('/future', methods=['GET'])
def getFutureGames():
    
    from nba_api.stats.endpoints import scheduleleaguev2
    from datetime import datetime, timedelta
    games = scheduleleaguev2.ScheduleLeagueV2()

    df = games.get_data_frames()[0]

    # good format
    df['gameDateTimeEst'] = pd.to_datetime(df['gameDateTimeEst'], format='%Y-%m-%dT%H:%M:%SZ')
    print(df['gameDateTimeEst'])
    # timezone to van
    df['gameDateTimeEst'] = df['gameDateTimeEst'] - timedelta(hours=3)
    # get get request date
    current_datetime = datetime.strptime(request.args['date'][:-1], "%Y-%m-%d %H:%M:%S")
    print(current_datetime)
    # get the day before that request day
    tomorrow = current_datetime + pd.Timedelta(days=1)
    # limit df to that request day
    df = df[df['gameDateTimeEst'].dt.date == tomorrow.date()]
    # limit columns to relevant
    df =df.loc[:, ['gameDateTimeEst', 'gameId', 'homeTeam_teamName', 'homeTeam_score', 'awayTeam_teamName', 'awayTeam_score', 'gameStatusText', 'homeTeam_teamTricode', 'awayTeam_teamTricode']]
    # sort entries by date
    df = df.sort_values(by='gameDateTimeEst')

    games_list = []

    for row in df.iterrows():
        game = {}

        if row[1]['homeTeam_teamTricode'] == 'UTA':
            awaytri = 'utah'
        elif row[1]['homeTeam_teamTricode'] == 'NOP':
            awaytri = 'no'
        else:
            awaytri = row[1]['homeTeam_teamTricode']

        if row[1]['awayTeam_teamTricode'] == 'UTA':
            hometri = 'utah'
        elif row[1]['awayTeam_teamTricode'] == 'NOP':
            hometri = 'no'
        else:
            hometri = row[1]['awayTeam_teamTricode']

        if (row[1]['gameStatusText'])[-2:] == 'ET':
            status = " N/A"
        else:
            status = row[1]['gameStatusText']

        game.update({'Title': row[1]['homeTeam_teamName'] + ' vs ' + row[1]['awayTeam_teamName']})
        game.update({'Game Score': str(row[1]['homeTeam_score']) +' - ' + str(row[1]['awayTeam_score'])})
        game.update({'Status': status})
        game.update({'Start Time': str((row[1]['gameDateTimeEst'].strftime("%a, %d %b %Y %I:%M %p")))})
        game.update({'GameID': row[1]['gameId']})
        game.update({'hometeamTricode': hometri})
        game.update({'awayteamTricode': awaytri})

        games_list.append(game)

    return games_list

@app.route('/game', methods=['GET'])
def getGameInfo():
    home = request.args['home']
    date = request.args['date']

    date = date[:10].replace('-','')

    print(date)

    # official nba site grab
    url = f"https://www.basketball-reference.com/boxscores/{date}{home}.html"
    # stats = pd.read_html(url)
    # game25=table25[7]
    # print(stats)

    return {'url': url,}

# -------------------------------------------------------------------------------------------------

def games(name):
    from nba_api.stats.endpoints import playergamelog
    from nba_api.stats.static import players

    # function to convert player name to player id
    nba_players = players.get_players()

    def get_player_id(player_name):
        player = next((p for p in nba_players if p['full_name'].lower() == player_name.lower()), None)
        return player['id'] if player else None

    # get id and search for games of last 2 years
    player_id = get_player_id(name)

    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
    df = gamelog.get_data_frames()[0]

    gamelog2 = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
    df2 = gamelog2.get_data_frames()[0]

    # merge this year + last year
    games = pd.concat([df, df2], axis=0)

    # only keep the columns i want
    games = games.loc[:, ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'PTS', 'AST','REB', 'BLK', 'STL', 'TOV', 'PLUS_MINUS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT']]
    games['GAME_DATE'] = games['GAME_DATE'].str.replace(',', '', regex=False)
    # print(games)


    # webscrape bball reference for image and accolades, and name (with correct capitalization)
    first = name.split(" ")[0].lower()
    last = name.split(" ")[1].lower()
    
    url = f"https://www.basketball-reference.com/players/{last[0]}/{last[0:5]}{first[0:2]}01/gamelog/2025#pgl_basic"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tag = f"<img src='https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png'>"
    name = name.title()

    accolades = ""
    for li in soup.find_all('li', class_=['poptip', 'all_star']):
        accolades += li.get_text(strip=True) + ", "
    accolades = accolades[:-2]

    
    return games, img_tag, name, accolades

def averages(game):
    points = pd.to_numeric(game['PTS'], errors='coerce').mean()
    assists = pd.to_numeric(game['AST'], errors='coerce').mean()
    rebounds = pd.to_numeric(game['REB'], errors='coerce').mean()
    blocks = pd.to_numeric(game['BLK'], errors='coerce').mean()
    steals = pd.to_numeric(game['STL'], errors='coerce').mean()

    average = ['Points: '+str(round(points, 2)),'Rebounds: '+str(round(rebounds, 2)),'Assists: '+str(round(assists, 2)),'Blocks: '+str(round(blocks, 2)),'Steals: '+str(round(steals, 2))]

    return average

def prediction(game):
    game = game.copy()
    game['MATCHUP'] = LabelEncoder().fit_transform(game['MATCHUP'])
    game['WL'] = LabelEncoder().fit_transform(game['WL'])

    for col in ['PTS', 'AST', 'REB']:
        game[f'{col}_prev'] = game[col].shift(1)
    game = game.dropna()

    features = ['MATCHUP', 'WL', 'MIN', 'PTS_prev', 'AST_prev', 'REB_prev']
    targets = ['PTS', 'AST', 'REB']
    models = {}
    predictions = {}

    game["MIN"] = pd.to_numeric(game["MIN"], errors="coerce")
    game["PTS_prev"] = pd.to_numeric(game["PTS_prev"], errors="coerce")
    game["AST_prev"] = pd.to_numeric(game["AST_prev"], errors="coerce")
    game["REB_prev"] = pd.to_numeric(game["REB_prev"], errors="coerce")


    for target in targets:
        X = game[features]
        y = game[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)
        model.fit(X_train, y_train)
        models[target] = model

        next_game_features = X.iloc[-1].values.reshape(1, -1)
        predictions[target] = round(models[target].predict(next_game_features)[0])

    return [f"PTS: {predictions['PTS']}", f"REB: {predictions['REB']}", f"AST: {predictions['AST']}"]



if __name__ == '__main__':
    app.run(port=420)
