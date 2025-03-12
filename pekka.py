from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from bs4 import BeautifulSoup
import requests

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
    games = pd.concat([df2, df], axis=0)
    games = games.iloc[::-1].reset_index(drop=True)

    # only keep the columns i want
    games = games.loc[:, ['GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'PTS', 'AST','REB', 'BLK', 'STL', 'TOV', 'PLUS_MINUS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT']]
    games['GAME_DATE'] = games['GAME_DATE'].str.replace(',', '', regex=False)
    # print(games)


    # webscrape bball reference for image and accolades, and name (with correct capitalization)
    first = name.split(" ")[0].lower()
    last = name.split(" ")[1].lower()
    
    url = f"https://www.basketball-reference.com/players/{last[0]}/{last[0:5]}{first[0:2]}01/gamelog/2025#pgl_basic"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find_all('li', class_=['poptip', 'all_star']):
            img_tag = soup.find_all('img')
            name = soup.find('h1')

            accolades = ""
            for li in soup.find_all('li', class_=['poptip', 'all_star']):
                accolades += li.get_text(strip=True) + ", "
            accolades = accolades[:-2]
        else:
            name = name
            img_tag=['','']
            accolades = ''
    
    return games, img_tag[1], name, accolades

def averages(game):
    points = pd.to_numeric(game['PTS'], errors='coerce').mean()
    assists = pd.to_numeric(game['AST'], errors='coerce').mean()
    rebounds = pd.to_numeric(game['REB'], errors='coerce').mean()
    blocks = pd.to_numeric(game['BLK'], errors='coerce').mean()
    steals = pd.to_numeric(game['STL'], errors='coerce').mean()

    average = ['Points: '+str(round(points, 2)),'Rebounds: '+str(round(rebounds, 2)),'Assists: '+str(round(assists, 2)),'Blocks: '+str(round(blocks, 2)),'Steals: '+str(round(steals, 2))]

    return average

def prediction(game, targets=['PTS', 'REB', 'AST', 'BLK', 'STL']):
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error

    game['Prev_PTS'] = game['PTS'].shift(1)
    game['Prev_AST'] = game['AST'].shift(1)
    game['Prev_TRB'] = game['REB'].shift(1)
    game['Prev_BLK'] = game['BLK'].shift(1)
    game['Prev_STL'] = game['STL'].shift(1)
    
    game = game.dropna(subset=['Prev_PTS', 'Prev_AST', 'Prev_TRB', 'Prev_BLK', 'Prev_STL'])
    
    X = game[['Prev_PTS', 'Prev_AST', 'Prev_TRB', 'Prev_BLK', 'Prev_STL']]

    predictions = []
    
    for target in targets:
        y = game[target]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, shuffle=False)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        next_game_features = X_test.iloc[-1].values.reshape(1, -1)
        predicted_value = model.predict(next_game_features)
        
        predictions.append(target + ': ' +str(round(predicted_value[0])))

    return predictions



if __name__ == '__main__':
    app.run(port=420)
