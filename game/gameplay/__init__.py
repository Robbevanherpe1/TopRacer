import pygame

from tracks import Track
from cars import Car
from constants.constants import *
from data.player_data import load_players

from gameplay.base_game import BaseGame
from gameplay.player_game import PlayerGame
from gameplay.event_game import EventGame
from gameplay.race_game import RaceGame


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.track = Track()
        
        # Create cars with different colors
        self.colors = [BLUE, RED, GREEN, YELLOW, PURPLE, CYAN, ORANGE]
        self.cars = []
        self.selected_car_index = 0
        
        # Track which cars are controllable by the racing engineer
        self.engineer_car_indices = []
        
        # Manufacturer properties
        self.player_team_manufacturer = "Ferrari"
        self.available_manufacturers = [
            "Ferrari", "Bentley", "BMW", "McLaren", 
            "Mercedes", "Nissan", "Porsche", "Renault"
        ]
        
        # Set up two special racing engineer cars
        # First engineer car - blue with special name
        engineer_car1 = Car(self.track, color=BLUE, name="Team Alpha")
        engineer_car1.can_push = True
        engineer_car1.is_engineer_car = True  # Add a flag to identify engineer cars
        self.cars.append(engineer_car1)
        self.engineer_car_indices.append(0)
        
        # Second engineer car - red with special name
        engineer_car2 = Car(self.track, color=RED, name="Team Omega")
        engineer_car2.can_push = True
        engineer_car2.is_engineer_car = True
        self.cars.append(engineer_car2)
        self.engineer_car_indices.append(1)
        
        # Set up three regular AI cars (no push capability)
        for i in range(3):
            color = self.colors[i+2]  # Start from 3rd color (green, yellow, purple)
            name = f"AI Car {i+1}"
            car = Car(self.track, color=color, name=name)
            car.can_push = False
            car.is_engineer_car = False
            # Set random setup for AI cars
            car.set_random_setup()
            self.cars.append(car)
        
        # Game state
        self.running = True
        self.race_time = 0
        self.message = "Welcome to TopRacer! Press SPACE to start/pause. Arrow keys to select car. P to push."
        self.message_timer = 300

        # Race settings
        self.MAX_LAPS = 5  # Race ends after 5 laps
        
        # Race positions
        self.race_positions = []  # Will store current race positions
        self.final_positions = []  # Will store final race positions when race ends
        self.race_finished = False  # Flag to indicate if race has finished

        # Camera position
        self.camera_x = 0
        self.camera_y = 0

        # Game state
        self.state = STATE_START_SCREEN
        
        # Waypoint visibility toggle
        self.show_waypoints = False

        # Button properties for end screen
        self.menu_button_rect = pygame.Rect(0, 0, 200, 60)  # Will position later
        
        # Customization screen properties
        self.start_race_button_rect = pygame.Rect(0, 0, 300, 70)  # Will position later
        self.setup_sliders = {}
        self.active_slider = None
        self.manufacturer_button_rect = pygame.Rect(0, 0, 155, 45)  # Manufacturer button
        
        # Manufacturer selection properties
        self.back_button_rect = pygame.Rect(0, 0, 300, 60)  # Back to garage button
        self.left_arrow_rect = pygame.Rect(0, 0, 60, 60)  # Left arrow for carousel
        self.right_arrow_rect = pygame.Rect(0, 0, 60, 60)  # Right arrow for carousel
        
        # Player stats - enhanced with proper rewards system
        self.player_points = 0
        self.player_team_rating = 0
        self.player_races_won = 0
        self.player_username = "Player1"
        
        # New stats for last race performance
        self.last_race_points_earned = 0
        self.last_race_xp_earned = 0
        
        # Car-specific upgrades for each garage (updated structure)
        self.car_upgrades = {}
        
        # Legacy upgrade variables - keep for backward compatibility
        self.engine_upgrade_level = 0
        self.tires_upgrade_level = 0
        self.aero_upgrade_level = 0
        
        # Upgrade costs - increases with each level
        self.base_upgrade_cost = 100
        self.upgrade_buttons = {}
        
        # Player account management
        self.players = load_players()
        self.available_player_names = list(self.players.keys())
        self.player_name = self.available_player_names[0] if self.available_player_names else "Team Alpha Racing"
        
        # Load player stats if available
        if self.player_name in self.players:
            self.player_points = self.players[self.player_name]["points"]
            self.player_team_rating = self.players[self.player_name]["team_rating"]
            self.player_races_won = self.players[self.player_name]["races_won"]
        
        # Account management in start screen
        self.adding_new_player = False
        self.new_player_name = ""
        self.selected_player_index = 0 if self.available_player_names else -1
        
        # Input field for new player
        self.input_active = False
        self.input_rect = pygame.Rect(0, 0, 300, 50)  # Will position later
        
        # Player management buttons
        self.player_buttons = []  # Will contain rects for each player (select/delete)
        self.add_player_button_rect = pygame.Rect(0, 0, 200, 50)  # Will position later
        self.delete_buttons = []  # Will contain rects for delete buttons
        
        # Initialize component controllers
        self.base_game = BaseGame(self)
        self.player_game = PlayerGame(self)
        self.event_game = EventGame(self)
        self.race_game = RaceGame(self)
        
    def save_current_player_stats(self):
        """Save the current player's stats to file"""
        return self.player_game.save_current_player_stats()
    
    def select_player(self, name):
        """Select a player and load their stats"""
        return self.player_game.select_player(name)
    
    def process_events(self, events):
        """Process pygame events passed from the main loop"""
        return self.event_game.process_events(events)
    
    # Keep the original handle_events for backward compatibility but make it call process_events
    def handle_events(self):
        """Legacy method - now just passes pygame events to process_events"""
        return self.event_game.handle_events()
    
    def update(self):
        """Update game state"""
        return self.race_game.update()

    def update_race_positions(self):
        """Calculate current race positions based on laps completed and distance to next waypoint"""
        return self.race_game.update_race_positions()

    def calculate_race_rewards(self):
        """Calculate points and experience earned based on race positions"""
        return self.race_game.calculate_race_rewards()
        
    def reset_race(self):
        """Reset race state to prepare for a new race"""
        return self.race_game.reset_race()