# Bot Discord - Notification de Défaite League of Legends

Ce bot Discord surveille les parties classées de joueurs prédéfinis sur League of Legends et envoie une notification dans un salon Discord dès qu'un joueur perd une partie.

## 🛠 Fonctionnalités
- Surveillance des matchs des joueurs spécifiés.
- Détection des défaites en mode Ranked Solo/Duo.
- Notification envoyée sur Discord avec les détails de la partie :
  - Mode de jeu
  - Champion joué
  - KDA (Kills/Deaths/Assists)
  - Perte de LP et rang actuel

## 📌 Prérequis
Avant d'exécuter le bot, assurez-vous d'avoir :
- Un serveur Discord avec un bot enregistré.
- Une clé API Riot valide.
- Python installé (3.8 ou plus recommandé).
- Les bibliothèques requises installées (voir ci-dessous).

## ⚙ Installation
1. Clonez ce dépôt ou copiez le code du bot.
```bash
git clone <url-du-dépôt>
cd <nom-du-dossier>
```
2. Installez les dépendances nécessaires :
```bash
pip install discord requests asyncio python-dotenv
```
3. Créez un fichier `.env` et ajoutez vos informations :
```
RIOT_API_KEY=VotreCléAPI
DISCORD_TOKEN=VotreTokenDiscord
CHANNEL_ID=VotreSalonID
```
4. Modifiez les joueurs à surveiller dans le script :
```python
NameTab = ["Joueur1", "Joueur2"]  # Remplacez par les pseudos
TagTab = ["TAG1", "TAG2"]  # Remplacez par les tags
IDTab = [123456789012345678, 987654321098765432]  # Remplacez par les ID Discord
```

## 🚀 Lancement du Bot
Exécutez simplement la commande suivante :
```bash
python bot.py
```

## 📝 Fonctionnement
- Le bot se connecte à Discord et surveille les joueurs définis.
- Il interroge périodiquement l'API Riot pour récupérer les dernières parties jouées.
- Lorsqu'une défaite est détectée en classé solo/duo, il envoie une notification dans le salon spécifié.
- La notification contient des détails sur la partie et la perte de LP.


