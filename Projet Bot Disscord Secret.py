import discord
import requests
import json
import asyncio
import os  # Pour utiliser les variables d'environnement

# 🔹 Clé API Riot et Discord (à définir dans les variables d'environnement)
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Remplace avec l'ID du salon Discord

# 🔹 Infos des joueurs
NameTab = ["Joueur1", "Joueur2"]  # Remplace avec tes vrais pseudos
TagTab = ["TAG1", "TAG2"]  # Remplace avec tes vrais tags
IDTab = [123456789012345678, 987654321098765432]  # Remplace avec les vrais ID Discord
LastGameTab = [0] * len(NameTab)
lpTab = [0] * len(NameTab)

headers = {"X-Riot-Token": RIOT_API_KEY}

# 🔹 Initialisation du bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_summoner_id(puuid):
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    response = requests.get(url, headers=headers)
    return response.json().get("id") if response.status_code == 200 else None

def get_rank_and_lp(summoner_id):
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur récupération du rank {response.status_code}: {response.text}")
        return "Non classé", 0
    
    rank_data = response.json()
    for queue in rank_data:
        if queue["queueType"] == "RANKED_SOLO_5x5":
            tier = queue['tier']
            rank = queue['rank']
            base_lp = queue["leaguePoints"]
            return f"{tier} {rank}", base_lp
    return "Non classé", 0

async def check_matches():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while not client.is_closed():
        for i in range(len(NameTab)):
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{NameTab[i]}/{TagTab[i]}"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                continue
            
            PUUID = response.json().get("puuid")
            urlHistorique = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{PUUID}/ids?start=0&count=1"
            historique = requests.get(urlHistorique, headers=headers)
            if historique.status_code != 200:
                continue

            matchId = historique.json()[0]
            if matchId == LastGameTab[i]:
                continue
            
            urlMatch = f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"
            match_response = requests.get(urlMatch, headers=headers)
            if match_response.status_code != 200:
                continue
            
            match_data = match_response.json()
            queue_id = match_data["info"]["queueId"]
            game_mode = {420: "Ranked Solo/Duo", 440: "Ranked Flex", 400: "Normal Draft"}.get(queue_id, "Autre")
            
            for player in match_data["info"]["participants"]:
                if player.get("riotIdGameName") == NameTab[i]:
                    if queue_id == 420 and not player["win"]:
                        message = f"@everyone 🎮 **Défaite pour <@{IDTab[i]}> !**\n"
                        message += f"🕹 **Mode de jeu** : {game_mode}\n"
                        message += f"🛡 **Champion** : {player['championName']}\n"
                        message += f"⚔ **KDA** : {player['kills']} / {player['deaths']} / {player['assists']}\n"
                        summoner_id = get_summoner_id(PUUID)
                        if summoner_id:
                            rank, current_lp = get_rank_and_lp(summoner_id)
                            lp_perdu = lpTab[i] - current_lp
                            lpTab[i] = current_lp
                            message += f"❌ **Défaite** : Il a perdu {lp_perdu} LP. Il est {rank}\n"
                        await channel.send(message)
                    
                    summoner_id = get_summoner_id(PUUID)
                    if summoner_id:
                        _, current_lp = get_rank_and_lp(summoner_id)
                        lpTab[i] = current_lp
                    
                    break
            
            LastGameTab[i] = matchId
        
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"✅ {client.user} est connecté !")
    client.loop.create_task(check_matches())

client.run(DISCORD_TOKEN)
