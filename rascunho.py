import requests
import pandas as pd
import datetime

# Cada equipe possui um ID, que deve ser incrementado no URL de API
ids_das_equipes = [2829]

# Cada campeonato tem um ID também
tournament_id = [7]

# Será utilizado para conseguir idades
current_date = datetime.date.today()

# Headers para acessar o Thunder Client
headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)"
    }

# Método para pegar os IDs dos Players, que serão usados futuramente
def get_player_ids(): 
    link = "https://api.sofascore.com/api/v1/team/{team}/unique-tournament/{tournament}/season/52162/top-players/overall"
    player_ids = []

    for tournament in tournament_id:
        for team in ids_das_equipes:
            reqUrl = link.format(team=team, tournament=tournament) 
            payload = ""
            response = requests.request("GET", reqUrl, data=payload, headers=headersList)
            data = response.json()

            # Navegar o JSON para puxar os IDs
            for jogador in data["topPlayers"]["rating"]:
                nome = jogador["player"]["name"]
                id_jogador = jogador["player"]["id"]
                player_ids.append((nome, id_jogador))

    return player_ids

player_ids = get_player_ids()

# Método para pegar as variáveis de interesse
def get_player_basic_info():
    link = "https://api.sofascore.com/api/v1/player/{jogador_id}"
    player_info = []

    for player in player_ids:
        nome = player[0]
        id = player[1]
        reqUrl = link.format(jogador_id=id)
        payload = ""
        response = requests.request("GET", reqUrl, data=payload, headers=headersList)
        data = response.json()["player"]

        # Extract player information and handle missing values
        club = data.get("team", {}).get("name", "")
        position = data.get("position", "")
        jersey_number = data.get("jerseyNumber", "")
        height = data.get("height", "")
        preferred_foot = data.get("preferredFoot", "")
        country = data.get("country", {}).get("name", "")
        
        birth_timestamp = data.get("dateOfBirthTimestamp")
        if birth_timestamp:
            birth = datetime.datetime.fromtimestamp(birth_timestamp)
            age = current_date.year - birth.year - ((current_date.month, current_date.day) < (birth.month, birth.day))
        else:
            age = ""
        
        # Append player information as a tuple
        player_info.append((nome, club, position, jersey_number, height, preferred_foot, country, age))

    # Create a DataFrame with one row
    df_info = pd.DataFrame(player_info, columns=["Name", "Club", "Position", "Jersey Number", "Height", "Preferred Foot", "Country", "Age"])

    return df_info

# Get player information for the specified player
df = get_player_basic_info()

# Display the DataFrame
print(df)


ids_das_equipes = [2829,2714, 2547,2999]