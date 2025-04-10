from player_data import update_player_stats, update_player_garage, get_player_garage, get_car_upgrades


class PlayerGame:
    """Player management component for handling player data, saving and loading"""
    
    def __init__(self, game):
        self.game = game
    
    def save_current_player_stats(self):
        """Save the current player's stats to file"""
        # First save the general player stats using the existing function
        update_player_stats(
            self.game.player_name,
            self.game.player_points,
            self.game.player_team_rating,
            self.game.player_races_won
        )
        
        # Save data for each engineer car individually based on their name (garage name)
        for car_idx in self.game.engineer_car_indices:
            car = self.game.cars[car_idx]
            garage_name = car.name  # Team Alpha or Team Omega
            
            # Create a dictionary with the car's setup
            setup = car.setup.copy()
            
            # Get car-specific upgrades for this garage
            upgrades = self.game.car_upgrades.get(garage_name, {
                "engine": 0,
                "tires": 0,
                "aero": 0
            })
            
            # Save the garage-specific car data with current manufacturer and upgrades
            update_player_garage(
                self.game.player_name,
                garage_name,
                car.manufacturer,
                setup,
                upgrades
            )
    
    def select_player(self, name):
        """Select a player and load their stats"""
        if name in self.game.players:
            self.game.player_name = name
            self.game.player_points = self.game.players[name]["points"]
            self.game.player_team_rating = self.game.players[name]["team_rating"]
            self.game.player_races_won = self.game.players[name]["races_won"]
            self.game.player_username = name  # Use player name as username
            
            # Initialize the car_upgrades dictionary
            self.game.car_upgrades = {}
            
            # Load data for each engineer car from its respective garage
            for car_idx in self.game.engineer_car_indices:
                car = self.game.cars[car_idx]
                garage_name = car.name  # Team Alpha or Team Omega
                
                # Load garage data for this car
                garage_data = get_player_garage(name, garage_name)
                
                # Apply the manufacturer
                if "manufacturer" in garage_data:
                    car.update_manufacturer(garage_data["manufacturer"])
                    
                    # Update team manufacturer in game from first car (Team Alpha)
                    if garage_name == "Team Alpha":
                        self.game.player_team_manufacturer = garage_data["manufacturer"]
                
                # Apply the setup if available
                if "setup" in garage_data:
                    setup = garage_data["setup"]
                    for key, value in setup.items():
                        if key in car.setup:
                            car.setup[key] = value
                
                # Get the car-specific upgrades for the current manufacturer
                manufacturer = car.manufacturer
                car_upgrades = get_car_upgrades(name, garage_name, manufacturer)
                
                # Store these upgrades in the game's car_upgrades dictionary
                if garage_name not in self.game.car_upgrades:
                    self.game.car_upgrades[garage_name] = {}
                
                # Store manufacturer-specific upgrades
                self.game.car_upgrades[garage_name] = car_upgrades
                
                # For backward compatibility, set the global upgrade levels from Team Alpha car
                if garage_name == "Team Alpha":
                    self.game.engine_upgrade_level = car_upgrades.get("engine", 0)
                    self.game.tires_upgrade_level = car_upgrades.get("tires", 0)
                    self.game.aero_upgrade_level = car_upgrades.get("aero", 0)
                
                # Update car performance based on loaded setup and upgrades
                car.update_performance_from_setup()