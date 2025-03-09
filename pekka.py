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
    game, img, player, accolades = games(name)
    average=averages(game)
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
    first =name.split(" ")[0].lower()
    last =name.split(" ")[1].lower()

    url = f"https://www.basketball-reference.com/players/{last[0]}/{last[0:5]}{first[0:2]}01/gamelog/2024#pgl_basic"
    
    try:
        tables = pd.read_html(url)

        games = tables[7]

        games = games.loc[:, ['Date', 'Tm', 'Opp', 'Unnamed: 7', 'PTS', 'AST','TRB', 'BLK', 'STL', '+/-', 
                        'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%']]

        games.rename(columns={'Unnamed: 7': 'Result'}, inplace=True)
        games = games[~games.isin(['Inactive']).any(axis=1)]
        games = games[~games.isin(['Did Not Play']).any(axis=1)]
        games = games[~games.isin(['Did Not Dress']).any(axis=1)]
        games = games[~games.isin(['PTS']).any(axis=1)]
    except:
        print('oops')

    url2 = f"https://www.basketball-reference.com/players/{last[0]}/{last[0:5]}{first[0:2]}01/gamelog/2025#pgl_basic"
    
    tables2 = pd.read_html(url2)

    games2 = tables2[7]

    games2 = games2.loc[:, ['Date', 'Tm', 'Opp', 'Unnamed: 7', 'PTS', 'AST','TRB', 'BLK', 'STL', '+/-', 
                      'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%']]

    games2.rename(columns={'Unnamed: 7': 'Result'}, inplace=True)
    games2 = games2[~games2.isin(['Inactive']).any(axis=1)]
    games2 = games2[~games2.isin(['Did Not Play']).any(axis=1)]
    games2 = games2[~games2.isin(['Did Not Dress']).any(axis=1)]
    games2 = games2[~games2.isin(['PTS']).any(axis=1)]


    try:
        games = pd.concat([games, games2], axis=0).reset_index(drop=True)
        games = games.iloc[::-1].reset_index(drop=True)
    except:
        games=games2
        games = games.iloc[::-1].reset_index(drop=True)
        print('woops')


    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        img_tag = soup.find_all('img')
        name = soup.find('h1')

        accolades = ""
    for li in soup.find_all('li', class_=['poptip', 'all_star']):
        accolades += li.get_text(strip=True) + ", "
    accolades = accolades[:-2]
    
    return games, img_tag[1], name, accolades

def averages(game):
    points = pd.to_numeric(game['PTS'], errors='coerce').mean()
    assists = pd.to_numeric(game['AST'], errors='coerce').mean()
    rebounds = pd.to_numeric(game['TRB'], errors='coerce').mean()
    blocks = pd.to_numeric(game['BLK'], errors='coerce').mean()
    steals = pd.to_numeric(game['STL'], errors='coerce').mean()

    average = ['Points: '+str(round(points, 2)),'Rebounds: '+str(round(rebounds, 2)),'Assists: '+str(round(assists, 2)),'Blocks: '+str(round(blocks, 2)),'Steals: '+str(round(steals, 2))]

    return average

def prediction(game, targets=['PTS', 'TRB', 'AST', 'BLK', 'STL']):
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error

    # Step 1: Prepare the data by creating lag features
    game['Prev_PTS'] = game['PTS'].shift(1)
    game['Prev_AST'] = game['AST'].shift(1)
    game['Prev_TRB'] = game['TRB'].shift(1)
    game['Prev_BLK'] = game['BLK'].shift(1)
    game['Prev_STL'] = game['STL'].shift(1)
    
    # Drop rows where lag values are NaN (first row will have NaN for lag features)
    game = game.dropna(subset=['Prev_PTS', 'Prev_AST', 'Prev_TRB', 'Prev_BLK', 'Prev_STL'])
    
    # Step 2: Define the feature variables (X)
    X = game[['Prev_PTS', 'Prev_AST', 'Prev_TRB', 'Prev_BLK', 'Prev_STL']]  # Features

    predictions = []
    
    # Step 3: Iterate over each target and train a model for it
    for target in targets:
        y = game[target]  # Target (we're predicting multiple variables)
        
        # Step 4: Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Step 5: Initialize and train the model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Step 6: Make predictions on the test set
        y_pred = model.predict(X_test)
        
        # Step 8: Make a prediction for the next game
        next_game_features = X_test.iloc[-1].values.reshape(1, -1)  # Get the features of the last row in the test set
        predicted_value = model.predict(next_game_features)
        
        predictions.append(target + ': ' +str(round(predicted_value[0])))
    
    return predictions  # Return all predictions as a dictionary



if __name__ == '__main__':
    app.run(port=420)
