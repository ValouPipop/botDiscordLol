import discord
import requests
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import random
import time

load_dotenv()

# 🔹 Clé API Riot et Discord 
RIOT_API_KEY_LOL = os.getenv('RIOT_API_KEY_LOL')
RIOT_API_KEY_TFT = os.getenv('RIOT_API_KEY_TFT')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Convertir en entier

URL = "https://botharem.onrender.com"

# 🔹 Infos des joueurs
# 🔹 Infos des joueurs
data = {
    "Player1": {
        "Tag": "TAG1",
        "puiid": None,
        "ID": 123456789012345678,
        "LastGame": 0,
        "LastGameTFT": 0,
        "lp": 0,
        "lpTFT": 0
    },
    "Player2": {
        "Tag": "TAG2",
        "puiid": None,
        "ID": 123456789012345678,
        "LastGame": 0,
        "LastGameTFT": 0,
        "lp": 0,
        "lpTFT": 0
    },
    "Player3": {
        "Tag": "TAG3",
        "puiid": None,
        "ID": 123456789012345678,
        "LastGame": 0,
        "LastGameTFT": 0,
        "lp": 0,
        "lpTFT": 0
    },
    "Player4": {
        "Tag": "TAG4",
        "puiid": None,
        "ID": 123456789012345678,
        "LastGame": 0,
        "LastGameTFT": 0,
        "lp": 0,
        "lpTFT": 0
    },
    "Player5": {
        "Tag": "TAG5",
        "puiid": None,
        "ID": 123456789012345678,
        "LastGame": 0,
        "LastGameTFT": 0,
        "lp": 0,
        "lpTFT": 0
    }
}




headers = {"X-Riot-Token": RIOT_API_KEY_LOL}
headerstft = {"X-Riot-Token": RIOT_API_KEY_TFT}

# 🔹 Initialisation du bot
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 🔹 Serveur Flask pour UptimeRobot
app = Flask('')

from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    print("✅ Ping reçu sur /")  # Log pour voir si UptimeRobot fonctionne
    return "Le bot est en ligne ! 🚀"

def run_flask():
    try:
        print("🔥 Démarrage du serveur Flask...")
        app.run(host="0.0.0.0", port=8080)
    except Exception as e:
        print(f"⚠️ Erreur dans le serveur Flask : {e}")

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

def auto_ping():
    while True:
        try:
            response = requests.get(URL)  # Ping avec GET au lieu de HEAD
            print(f"🔄 Auto-ping envoyé, statut : {response.status_code}")
        except Exception as e:
            print(f"⚠️ Erreur dans l'auto-ping : {e}")
        time.sleep(10)  # Attendre 5 minutes avant le prochain ping

# Lancer l'auto-ping en parallèle
from threading import Thread
Thread(target=auto_ping, daemon=True).start()


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
            tier_bonus = {"BRONZE": 400, "SILVER": 800, "GOLD": 1200, "PLATINUM": 1600, "EMERALD": 1800, "DIAMOND": 2000, "MASTER": 2400}
            additional_lp = {"IV": 0, "III": 100, "II": 200, "I": 300}.get(rank, 0)
            return f"{tier} {rank}", base_lp + additional_lp + tier_bonus.get(tier, 0)
    return "Non classé", 0

def setPuiidTab():
    global data
    for player, info in data.items():
        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player}/{info['Tag']}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Erreur récupération PUUID pour {player} ({response.status_code}): {response.text}")
            continue

        response_data = response.json()  # Renommé pour éviter de redéfinir la variable 'data'
        if "puuid" in response_data:
            info["puiid"] = response_data["puuid"]
            print(f"✅ PUUID récupéré pour {player} : {info['puiid']}")

        else:
            print(f"⚠️ Aucun PUUID trouvé pour {player}")

def setLastGameTab():
    global data
    for player, info in data.items():
        if not f"{info['puiid']}":
            print(f"⚠️ PUUID introuvable pour {player}")
            continue

        # Utilisation de guillemets simples pour éviter les conflits avec les doubles guillemets
        urlHistorique = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{info['puiid']}/ids?start=0&count=1"
        response = requests.get(urlHistorique, headers=headers)

        if response.status_code != 200:
            print(f"❌ Erreur récupération historique ({response.status_code}): {response.text}")
            continue

        match_list = response.json()
        if not match_list:
            print(f"⚠️ Aucun match trouvé pour {player}")
            continue

        info["LastGame"] = match_list[0]  # ✅ Correction ici
        print(f"✅ Match initialisé pour {player} : {info['LastGame']}")


def setLpTab():
    for player, info in data.items():
        summoner_id = get_summoner_id(info['puiid'])  
        if not summoner_id:
            print(f"⚠️ Impossible de récupérer l'ID du joueur {player}")
            continue  # Passe au joueur suivant

        rank, current_lp = get_rank_and_lp(summoner_id)
        info['lp'] = current_lp

        print(f"✅ {player} est {rank} avec {current_lp} LP")  # Debug dans la console


async def check_matches():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        for player, info in data.items():
            urlHistorique = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{info['puiid']}/ids?start=0&count=1"
            historique = requests.get(urlHistorique, headers=headers)
            if historique.status_code != 200:
                print(f"Erreur {historique.status_code}: {historique.text}")
                continue

            if not historique.json():
                print(f"Aucun match trouvé pour {player}")
                continue

            matchId = historique.json()[0]
            if matchId == info['LastGame']:
                continue

            urlMatch = f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchId}"
            match_response = requests.get(urlMatch, headers=headers)
            if match_response.status_code != 200:
                print(f"Erreur {match_response.status_code}: {match_response.text}")
                continue

            match_data = match_response.json()
            queue_id = match_data["info"].get("queueId", 0)
            game_mode = {420: "Ranked Solo/Duo", 440: "Ranked Flex", 400: "Normal Draft", 430: "Normal Blind", 450: "ARAM", 700: "Clash", 1700: "Arena"}.get(queue_id, "Autre")

            for player in match_data["info"]["participants"]:
                if player.get("puuid") == info["puiid"]:

                    if not player["win"]:
                        if queue_id == 420:  # Vérification si c'est une partie classée en solo/duo
                            summoner_id = get_summoner_id(info["puiid"])
                            rank, current_lp = get_rank_and_lp(summoner_id) if summoner_id else ("Non classé", info['lp'])
                            lp_perdu = info['lp'] - current_lp
                            info['lp'] = current_lp
                            message = f"🎮 **Nouvelle défaite pour <@{info['ID']}> !**\n🕹 **Mode** : {game_mode}\n⚔ **KDA** : {player['kills']} / {player['deaths']} / {player['assists']}\n❌ **Défaite** : LP perdu {lp_perdu} LP. Rang: {rank}\n------------------------------------------------------------"
                            await channel.send(message)
                            nombre = random.randint(1, 22)
                            await channel.send(file=discord.File(f'images/{nombre}.jpg'))
                        else:
                            lp_perdu = "O pas ranked"
                            message = f"🎮 **Nouvelle défaite pour <@{info['ID']}> !**\n🕹 **Mode** : {game_mode}\n⚔ **KDA** : {player['kills']} / {player['deaths']} / {player['assists']}\n❌ **Défaite** \n------------------------------------------------------------"
                            await channel.send(message)
                            nombre = random.randint(1, 22)
                            await channel.send(file=discord.File(f'images/{nombre}.jpg'))
                    break

            summoner_id = get_summoner_id(info["puiid"])
            rank, current_lp = get_rank_and_lp(summoner_id) if summoner_id else ("Non classé", info['lp'])   
            info['lp'] = current_lp
            info['LastGame'] = matchId
            await asyncio.sleep(1)
        await asyncio.sleep(60)

        
# 🔹 Fonction check_matchesTFT modifiée
async def check_matchesTFT():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        for player, info in data.items():
            urlHistorique = f"https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{info['puiid']}/ids?start=0&count=1"
            historique = requests.get(urlHistorique, headers=headerstft)
            if historique.status_code != 200:
                print(f"Erreur {historique.status_code}: {historique.text}")
                continue

            if not historique.json():
                print(f"Aucun match trouvé pour {player}")
                continue

            matchId = historique.json()[0]
            if matchId == info['LastGameTFT']:
                continue

            urlMatch = f"https://europe.api.riotgames.com/tft/match/v1/matches/{matchId}"
            match_response = requests.get(urlMatch, headers=headerstft)
            if match_response.status_code != 200:
                print(f"Erreur {match_response.status_code}: {match_response.text}")
                continue

            match_data = match_response.json()

            for player in match_data["info"]["participants"]:
                if player.get("puuid") == info["puiid"]:
                    if not player["placement"] < 4:
                            message = f"🎮 **Nouvelle défaite pour <@{info['ID']}> !**\n🕹 **Mode** : TFT\n⚔ **PLACE** : {player['placement']} \n------------------------------------------------------------"
                            await channel.send(message)
                            nombre = random.randint(1, 22)
                            await channel.send(file=discord.File(f'images/{nombre}.jpg'))

                    break

            info["LastGameTFT"] = matchId
            await asyncio.sleep(2)
        await asyncio.sleep(60)

setPuiidTab()
asyncio.sleep(1)
setLastGameTab()
asyncio.sleep(1)
setLpTab()
asyncio.sleep(1)


@client.event
async def on_ready():
    print(f"✅ {client.user} est connecté !")
    client.loop.create_task(check_matches())

keep_alive()
client.run(DISCORD_TOKEN)
