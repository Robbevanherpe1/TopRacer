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
            "garages": {
                "Team Alpha": {
                    "manufacturer": "Ferrari",
                    "setup": {
                        "Engine": 5,
                        "Tires": 5,
                        "Aerodynamics": 5,
                        "Handling": 5,
                        "Brakes": 5
                    },
                    "cars": {
                        "Ferrari": {
                            "upgrades": {
                                "engine": 0,
                                "tires": 0,
                                "aero": 0
                            }
                        }
                    }
                },
                "Team Omega": {
                    "manufacturer": "Ferrari",
                    "setup": {
                        "Engine": 5,
                        "Tires": 5,
                        "Aerodynamics": 5,
                        "Handling": 5,
                        "Brakes": 5
                    },
                    "cars": {
                        "Ferrari": {
                            "upgrades": {
                                "engine": 0,
                                "tires": 0,
                                "aero": 0
                            }
                        }
                    }
                }
            },
            # Keep current_manufacturer and cars for backward compatibility
            "current_manufacturer": "Ferrari",
            "cars": {
                "Ferrari": {
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

def update_player_garage(name, garage_name, manufacturer=None, setup=None, upgrades=None):
    """
    Update a specific garage for a player with manufacturer, setup and upgrades
    
    Args:
        name (str): Player name
        garage_name (str): Garage name (Team Alpha or Team Omega)
        manufacturer (str, optional): Car manufacturer name
        setup (dict, optional): Car setup values
        upgrades (dict, optional): Upgrade levels
    """
    players = load_players()
    if name not in players:
        add_player(name)
    
    # Make sure the garages structure exists
    if "garages" not in players[name]:
        players[name]["garages"] = {
            "Team Alpha": {
                "manufacturer": "Ferrari",
                "setup": {
                    "Engine": 5, "Tires": 5, "Aerodynamics": 5, "Handling": 5, "Brakes": 5
                },
                "cars": {
                    "Ferrari": {
                        "upgrades": {"engine": 0, "tires": 0, "aero": 0}
                    }
                }
            },
            "Team Omega": {
                "manufacturer": "Ferrari",
                "setup": {
                    "Engine": 5, "Tires": 5, "Aerodynamics": 5, "Handling": 5, "Brakes": 5
                },
                "cars": {
                    "Ferrari": {
                        "upgrades": {"engine": 0, "tires": 0, "aero": 0}
                    }
                }
            }
        }
    
    # Make sure this specific garage exists
    if garage_name not in players[name]["garages"]:
        players[name]["garages"][garage_name] = {
            "manufacturer": "Ferrari",
            "setup": {
                "Engine": 5, "Tires": 5, "Aerodynamics": 5, "Handling": 5, "Brakes": 5
            },
            "cars": {
                "Ferrari": {
                    "upgrades": {"engine": 0, "tires": 0, "aero": 0}
                }
            }
        }
    
    # Update manufacturer if provided
    if manufacturer:
        # Save the old manufacturer
        old_manufacturer = players[name]["garages"][garage_name].get("manufacturer", "Ferrari")
        
        # Update to new manufacturer
        players[name]["garages"][garage_name]["manufacturer"] = manufacturer
        
        # Ensure the cars dictionary exists
        if "cars" not in players[name]["garages"][garage_name]:
            players[name]["garages"][garage_name]["cars"] = {}
        
        # Make sure this manufacturer exists in cars
        if manufacturer not in players[name]["garages"][garage_name]["cars"]:
            # Create default upgrades for this manufacturer
            players[name]["garages"][garage_name]["cars"][manufacturer] = {
                "upgrades": {"engine": 0, "tires": 0, "aero": 0}
            }
    else:
        # Use existing manufacturer
        manufacturer = players[name]["garages"][garage_name].get("manufacturer", "Ferrari")
    
    # Update setup if provided
    if setup:
        players[name]["garages"][garage_name]["setup"] = setup
    
    # Update upgrades if provided and store them with the specific manufacturer
    if upgrades and manufacturer:
        # Ensure the cars structure exists
        if "cars" not in players[name]["garages"][garage_name]:
            players[name]["garages"][garage_name]["cars"] = {}
        
        # Ensure this manufacturer exists in cars
        if manufacturer not in players[name]["garages"][garage_name]["cars"]:
            players[name]["garages"][garage_name]["cars"][manufacturer] = {}
        
        # Update upgrades for specific manufacturer
        players[name]["garages"][garage_name]["cars"][manufacturer]["upgrades"] = upgrades
    
    save_players(players)
    
    return players[name]["garages"][garage_name]

def get_player_garage(name, garage_name):
    """
    Get data for a specific garage
    
    Args:
        name (str): Player name
        garage_name (str): Garage name (Team Alpha or Team Omega)
    
    Returns:
        dict: Garage data including manufacturer, setup and upgrades
    """
    players = load_players()
    if name not in players:
        add_player(name)
        players = load_players()
    
    # Make sure garages structure exists
    if "garages" not in players[name]:
        # Try to migrate legacy data if it exists
        if "cars" in players[name] and "current_manufacturer" in players[name]:
            manufacturer = players[name]["current_manufacturer"]
            setup = None
            upgrades = None
            
            if manufacturer in players[name]["cars"]:
                if "setup" in players[name]["cars"][manufacturer]:
                    setup = players[name]["cars"][manufacturer]["setup"]
                if "upgrades" in players[name]["cars"][manufacturer]:
                    upgrades = players[name]["cars"][manufacturer]["upgrades"]
            
            # Create garages with migrated data
            players[name]["garages"] = {
                "Team Alpha": {
                    "manufacturer": manufacturer,
                    "setup": setup or {
                        "Engine": 5, "Tires": 5, "Aerodynamics": 5, "Handling": 5, "Brakes": 5
                    },
                    "cars": {
                        manufacturer: {
                            "upgrades": upgrades or {
                                "engine": 0, "tires": 0, "aero": 0
                            }
                        }
                    }
                },
                "Team Omega": {
                    "manufacturer": manufacturer,
                    "setup": setup or {
                        "Engine": 5, "Tires": 5, "Aerodynamics": 5, "Handling": 5, "Brakes": 5
                    },
                    "cars": {
                        manufacturer: {
                            "upgrades": upgrades or {
                                "engine": 0, "tires": 0, "aero": 0
                            }
                        }
                    }
                }
            }
            save_players(players)
        else:
            # Just create default garages
            update_player_garage(name, garage_name)
            players = load_players()
    
    # Make sure this specific garage exists
    if garage_name not in players[name]["garages"]:
        update_player_garage(name, garage_name)
        players = load_players()
    
    return players[name]["garages"][garage_name]

def get_car_upgrades(name, garage_name, manufacturer):
    """
    Get upgrades for a specific car in a garage
    
    Args:
        name (str): Player name
        garage_name (str): Garage name (Team Alpha or Team Omega)
        manufacturer (str): Car manufacturer name
    
    Returns:
        dict: Upgrades for the specified car
    """
    garage_data = get_player_garage(name, garage_name)
    
    # Check if this car exists in the garage's cars
    if "cars" in garage_data and manufacturer in garage_data["cars"]:
        # Return upgrades for this specific car
        return garage_data["cars"][manufacturer].get("upgrades", {
            "engine": 0, "tires": 0, "aero": 0
        })
    
    # Return default upgrades if car doesn't exist yet
    return {"engine": 0, "tires": 0, "aero": 0}
