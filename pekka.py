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
