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
            "current_manufacturer": "Ferrari",  # Default manufacturer
            "cars": {
                "Ferrari": {  # Default car
                    "setup": {
                        "Engine": 5,
                        "Tires": 5,
                        "Aerodynamics": 5,
                        "Handling": 5,
                        "Brakes": 5
                    },
                    "upgrades": {
                        "engine": 0,
                        "tires": 0,
                        "aero": 0
                    }
                }
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
    
    # Get current manufacturer
    current_manufacturer = players[name].get("current_manufacturer", "Ferrari")
    
    # Save car upgrades to the current manufacturer's car
    if upgrades:
        # Make sure the cars structure exists
        if "cars" not in players[name]:
            players[name]["cars"] = {}
            
        # Make sure current manufacturer exists in cars
        if current_manufacturer not in players[name]["cars"]:
            players[name]["cars"][current_manufacturer] = {
                "setup": {
                    "Engine": 5,
                    "Tires": 5,
                    "Aerodynamics": 5,
                    "Handling": 5,
                    "Brakes": 5
                },
                "upgrades": {
                    "engine": 0,
                    "tires": 0,
                    "aero": 0
                }
            }
        
        # Update upgrades for current manufacturer's car
        players[name]["cars"][current_manufacturer]["upgrades"]["engine"] = upgrades.get("engine", 0)
        players[name]["cars"][current_manufacturer]["upgrades"]["tires"] = upgrades.get("tires", 0)
        players[name]["cars"][current_manufacturer]["upgrades"]["aero"] = upgrades.get("aero", 0)
    
    save_players(players)

def update_player_car(name, manufacturer, setup=None, upgrades=None):
    """
    Update or add a car for a player with its setup and upgrades
    
    Args:
        name (str): Player name
        manufacturer (str): Car manufacturer name
        setup (dict, optional): Car setup values for engine, tires, etc.
        upgrades (dict, optional): Upgrade levels for engine, tires, and aero
    """
    players = load_players()
    if name not in players:
        add_player(name)
    
    # Update current manufacturer
    players[name]["current_manufacturer"] = manufacturer
    
    # Initialize cars dict if it doesn't exist
    if "cars" not in players[name]:
        players[name]["cars"] = {}
    
    # Initialize manufacturer entry if it doesn't exist
    if manufacturer not in players[name]["cars"]:
        players[name]["cars"][manufacturer] = {
            "setup": {
                "Engine": 5,
                "Tires": 5,
                "Aerodynamics": 5,
                "Handling": 5,
                "Brakes": 5
            },
            "upgrades": {
                "engine": 0,
                "tires": 0,
                "aero": 0
            }
        }
    
    # Update setup if provided
    if setup:
        players[name]["cars"][manufacturer]["setup"] = setup
    
    # Update upgrades if provided
    if upgrades:
        players[name]["cars"][manufacturer]["upgrades"] = upgrades
    
    save_players(players)
