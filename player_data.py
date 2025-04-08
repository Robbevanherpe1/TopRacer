import json
import os
from pathlib import Path

# Define save file location
SAVE_DIR = Path.home() / ".topracer"
SAVE_FILE = SAVE_DIR / "players.json"

# Ensure save directory exists
if not SAVE_DIR.exists():
    SAVE_DIR.mkdir(parents=True)

def save_players(players):
    """Save player data to file"""
    with open(SAVE_FILE, 'w') as f:
        json.dump(players, f, indent=2)

def load_players():
    """Load player data from file"""
    if not SAVE_FILE.exists():
        # Return default player if no save file exists
        return {
            "Team Alpha Racing": {
                "points": 0,
                "team_rating": 0,
                "races_won": 0
            }
        }
    
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading player data: {e}")
        return {}

def add_player(name):
    """Add a new player with default stats"""
    players = load_players()
    if name and name not in players:
        players[name] = {
            "points": 0,
            "team_rating": 0,
            "races_won": 0,
            "upgrades": {
                "engine": 0,
                "tires": 0,
                "aero": 0
            }
        }
        save_players(players)
        return True
    return False

def delete_player(name):
    """Delete a player from saved data"""
    players = load_players()
    if name in players:
        del players[name]
        save_players(players)
        return True
    return False

def update_player_stats(name, points, team_rating, races_won, upgrades=None):
    """Update player stats and save to file"""
    players = load_players()
    if name not in players:
        add_player(name)
    
    players[name]["points"] = points
    players[name]["team_rating"] = team_rating
    players[name]["races_won"] = races_won
    
    # Save car upgrades
    if upgrades:
        if "upgrades" not in players[name]:
            players[name]["upgrades"] = {}
        players[name]["upgrades"]["engine"] = upgrades.get("engine", 0)
        players[name]["upgrades"]["tires"] = upgrades.get("tires", 0)
        players[name]["upgrades"]["aero"] = upgrades.get("aero", 0)
    
    save_players(players)
