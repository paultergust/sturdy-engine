import requests

player_api = 'https://lichess.org/api/player'

output = requests.get(player_api)

print(output.json())
