import requests
import pandas as pd

# Cada equipe possui um ID, que deve ser incrementado no URL de API
ids_das_equipes = [2829,2999,2714,2547]

# Headers para acessar o Thunder Client
headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)"
    }

# Método para pegar os IDs dos Players, que seriam usados futuramente
def get_player_ids(): 
    
    link = "https://api.sofascore.com/api/v1/team/{team}/unique-tournament/7/season/52162/top-players/overall"
    player_data = []


    for team in ids_das_equipes:
        reqUrl= link.format(team=team) 
        payload = ""
        response = requests.request("GET", reqUrl, data=payload, headers=headersList)
        data = response.json()['topPlayers']

        for jogador in data["rating"]:
            nome = jogador["player"]["slug"]
            id_jogador = jogador["player"]["id"]
            player_data.append((nome, id_jogador))
        print("ihaa")
    return player_data

player_data = get_player_ids()

df = pd.DataFrame(player_data, columns=[player_data])

# Cada campeonato tem um ID também
id_do_campeonato = [7]

# Esse é URL de base para as APIs, encontrado no código fonte
base_url = "https://api.sofascore.com/api/v1/team/{team_id}/unique-tournament/{tournament_id}/season/52162/top-players/overall"

# Dataframe inicial com variáveis dos jogadores
df = pd.DataFrame()



for team_id in ids_das_equipes:
    
    #
    reqUrl= base_url.format(team_id=team_id, tournament_id=id_do_campeonato)  
    headersList = {
    "Accept": "*/*",
    "User-Agent": "Thunder Client (https://www.thunderclient.com)" 
    }

    payload = ""

    response = requests.request("GET", reqUrl, data=payload, headers=headersList)
    estat = response.json()['topPlayers']

    data = [estat]

    player_data_list = []

    for player_data in data:
        for rating_stat in player_data['rating']:
            player_info = rating_stat['player']
            player_name = player_info['name']
            player_position = player_info['position']

            player_stats = {
                'name': player_name,
                'position': player_position,
            }

            for stat_type, stats in player_data.items():
                for stat in stats:
                    if stat['player']['name'] == player_name:  
                        for stat_key, stat_value in stat['statistics'].items():
                            col_name = f"{stat_type}_{stat_key}"
                            player_stats[col_name] = stat_value
            player_data_list.append(player_stats)

    nova_df = pd.DataFrame(player_data_list)

    df = pd.concat([df, nova_df], ignore_index=True)

cols_to_keep = [col for col in df.columns if '_type' not in col]
df = df[cols_to_keep]
cols_to_keep = [col for col in df.columns if '_appearances' not in col]
df = df[cols_to_keep]
df.to_excel('Jogadores_Grupo_C.xlsx', index=False)
print(df)


