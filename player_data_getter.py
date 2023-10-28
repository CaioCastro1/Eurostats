import requests
import pandas as pd
import datetime

# Cada equipe possui um ID, que deve ser incrementado no URL de API
ids_das_equipes = [2829,2714, 2547,2999]

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

        # Pegar as informações, reconhecendo que as vezes o jogador não tem uma informação (sofri muito com alguns reservas do Leverkusen)
        club = data.get("team", {}).get("name", "")
        position = data.get("position", "")
        jersey_number = data.get("jerseyNumber", "")
        height = data.get("height", "")
        preferred_foot = data.get("preferredFoot", "Right")
        country = data.get("country", {}).get("name", "")
        
        birth_timestamp = data.get("dateOfBirthTimestamp")
        if birth_timestamp:
            birth = datetime.datetime.fromtimestamp(birth_timestamp)
            age = current_date.year - birth.year - ((current_date.month, current_date.day) < (birth.month, birth.day))
        else:
            age = ""
        
        # Criando a tupla que vai ser posta no df
        player_info.append((nome, club, position, jersey_number, height, preferred_foot, country, age))

    df_info = pd.DataFrame(player_info, columns=["Name", "Club", "Position", "Jersey Number", "Height", "Preferred Foot", "Country", "Age"])
    return df_info

def get_player_data():
    link = "https://api.sofascore.com/api/v1/team/{team_id}/unique-tournament/{tournament_id}/season/52162/top-players/overall"
    player_data_list = []
    df = pd.DataFrame()

    for tournament in tournament_id:
        for team in ids_das_equipes:
            reqUrl = link.format(team_id=team, tournament_id=tournament) 
            payload = ""
            response = requests.request("GET", reqUrl, data=payload, headers=headersList)
            estat = response.json()['topPlayers']
            data = [estat]

            for player_data in data:
                for rating_stat in player_data['rating']:
                    player_info = rating_stat['player']
                    player_name = player_info['name']
                    player_stats = {
                        'Name': player_name
                    }

                    for stat_type, stats in player_data.items():
                        for stat in stats:
                            if stat['player']['name'] == player_name:
                                for stat_key, stat_value in stat['statistics'].items():
                                    if stat_type == stat_key:
                                        col_name = convert_camel_case_to_readable(stat_key)
                                        player_stats[col_name] = stat_value

                    for stat_type, stats in player_data.items():
                        for stat in stats:
                            if stat['player']['name'] == player_name:
                                for stat_key, stat_value in stat['statistics'].items():
                                      # Quase esqueci dessas!
                                    if "Percentage" in stat_key:
                                        col_name = convert_camel_case_to_readable(stat_key)
                                        player_stats[col_name] = stat_value

                    player_data_list.append(player_stats)

    df = pd.DataFrame(player_data_list)
    df = df.fillna(0)
    return df  

# Vai ser usado para resolver nomenclatura
def convert_camel_case_to_readable(s):
    result = ""

    for char in s:
        if char.isupper():
            result += " " + char
        else:
            result += char

    return result.strip().capitalize()

df_data = get_player_data()

df_info = get_player_basic_info()

# Merge para juntar as duas tabelas
df_final = pd.merge(df_info, df_data, on='Name', how='left')

df_final.to_excel('Jogadores_Grupo_C.xlsx', index=False)

print(df_final)

        









