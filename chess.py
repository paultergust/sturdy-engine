import requests
import csv
from datetime import datetime, timedelta


def get_top_players(count=50, game_type='classical'):

    url = f'https://lichess.org/api/player/top/{count}/{game_type}'
    response = requests.get(url, headers={"Accept": "application/json"})

    if response.status_code != 200:
        raise Exception(f"Failed getting top {count} usernames: {response.status_code} - {response.text}")

    return response.json()['users']


def get_30_day_history(usernames):
    results = []
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)

    for username in usernames:
        url = f"https://lichess.org/api/user/{username}/rating-history"
        response = requests.get(url, headers={"Accept": "application/json"})

        if response.status_code != 200:
            results.append({
                "username": username,
                "score_today": "Error",
                "score_30_days_ago": f"Failed to fetch data: {response.status_code}"
            })
            continue

        rating_data = response.json()

        # Find the classical game type history
        for entry in rating_data:
            if entry['name'].lower() == "classical":
                history = entry['points']  # List of [timestamp, rating]
                ratings = {
                    datetime.utcfromtimestamp(timestamp / 1000).date(): rating
                    for timestamp, rating in history
                }

                results.append({
                    "username": username,
                    "score_today": ratings.get(today, "N/A"),
                    "score_30_days_ago": ratings.get(thirty_days_ago, "N/A")
                })
                break
        else:
            results.append({
                "username": username,
                "score_today": "N/A",
                "score_30_days_ago": "No data for classical mode"
            })

    return results


def create_csv(players, filename='top_players_history.csv'):
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        field = ['username', 'score_30_days_ago', 'score_today']
        writer.writerow(field)
        for player in players:
            writer.writerow([player['username'], player['score_today'], player['score_30_days_ago']])


if __name__ == '__main__':
    players = get_top_players()
    for player in players:
        print(player['username'])
    top_player = players[0]
    history_data = get_30_day_history(top_player['username'])
    print(history_data)
