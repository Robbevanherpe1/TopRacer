import pygame
import random
import math
from track import Track
from car import Car
from constants import *
from player_data import load_players, update_player_stats, update_player_car

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
        
    def save_current_player_stats(self):
        """Save the current player's stats to file"""
        # Import the updated player_data functions
        from player_data import update_player_stats, update_player_garage
        
        # First save the general player stats using the existing function
        update_player_stats(
            self.player_name,
            self.player_points,
            self.player_team_rating,
            self.player_races_won
        )
        
        # Save data for each engineer car individually based on their name (garage name)
        for car_idx in self.engineer_car_indices:
            car = self.cars[car_idx]
            garage_name = car.name  # Team Alpha or Team Omega
            
            # Create a dictionary with the car's setup
            setup = car.setup.copy()
            
            # Get car-specific upgrades for this garage
            upgrades = self.car_upgrades.get(garage_name, {
                "engine": 0,
                "tires": 0,
                "aero": 0
            })
            
            # Save the garage-specific car data with current manufacturer and upgrades
            update_player_garage(
                self.player_name,
                garage_name,
                car.manufacturer,
                setup,
                upgrades
            )
    
    def select_player(self, name):
        """Select a player and load their stats"""
        if name in self.players:
            self.player_name = name
            self.player_points = self.players[name]["points"]
            self.player_team_rating = self.players[name]["team_rating"]
            self.player_races_won = self.players[name]["races_won"]
            self.player_username = name  # Use player name as username
            
            # Import player_data functions
            from player_data import get_player_garage, get_car_upgrades
            
            # Initialize the car_upgrades dictionary
            self.car_upgrades = {}
            
            # Load data for each engineer car from its respective garage
            for car_idx in self.engineer_car_indices:
                car = self.cars[car_idx]
                garage_name = car.name  # Team Alpha or Team Omega
                
                # Load garage data for this car
                garage_data = get_player_garage(name, garage_name)
                
                # Apply the manufacturer
                if "manufacturer" in garage_data:
                    car.update_manufacturer(garage_data["manufacturer"])
                    
                    # Update team manufacturer in game from first car (Team Alpha)
                    if garage_name == "Team Alpha":
                        self.player_team_manufacturer = garage_data["manufacturer"]
                
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
                if garage_name not in self.car_upgrades:
                    self.car_upgrades[garage_name] = {}
                
                # Store manufacturer-specific upgrades
                self.car_upgrades[garage_name] = car_upgrades
                
                # For backward compatibility, set the global upgrade levels from Team Alpha car
                if garage_name == "Team Alpha":
                    self.engine_upgrade_level = car_upgrades.get("engine", 0)
                    self.tires_upgrade_level = car_upgrades.get("tires", 0)
                    self.aero_upgrade_level = car_upgrades.get("aero", 0)
                
                # Update car performance based on loaded setup and upgrades
                car.update_performance_from_setup()
    
    def process_events(self, events):
        """Process pygame events passed from the main loop"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                global SCREEN_WIDTH, SCREEN_HEIGHT
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
            # Handle mouse clicks for buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if self.state == STATE_RACE_END:
                    # Check if Return to Customization button was clicked
                    if self.menu_button_rect.collidepoint(event.pos):
                        # Reset the race and go to customization screen
                        self.reset_race()
                        self.state = STATE_CUSTOMIZATION
                        self.message = "Customize your cars for the next race"
                        self.message_timer = 180
                elif self.state == STATE_CUSTOMIZATION:
                    # Check if Start Race button was clicked
                    if self.start_race_button_rect.collidepoint(event.pos):
                        # Check if BOTH engineer cars have balanced setup (sum of all values equals 25)
                        all_balanced = True
                        unbalanced_cars = []
                        
                        for car_idx in self.engineer_car_indices:
                            car = self.cars[car_idx]
                            total_balance = sum(car.setup.values())
                            if total_balance != 25:
                                all_balanced = False
                                unbalanced_cars.append(car.name)
                        
                        if all_balanced and hasattr(self, 'race_button_enabled') and self.race_button_enabled:
                            self.state = STATE_RACING
                            self.message = "Race started!"
                            self.message_timer = 180
                        else:
                            self.message = f"All cars must have exactly 25 setup points to start! Check: {', '.join(unbalanced_cars)}" if unbalanced_cars else "Car setups must be balanced!"
                            self.message_timer = 180
                    
                    # Check if Menu button was clicked
                    if hasattr(self, 'menu_button_rect') and self.menu_button_rect.collidepoint(event.pos):
                        if hasattr(self, 'menu_button_enabled') and self.menu_button_enabled:
                            # Save current player stats before returning to start screen
                            self.save_current_player_stats()
                            # Return to start screen
                            self.state = STATE_START_SCREEN
                            self.message = "Returned to main menu"
                            self.message_timer = 180
                    
                    # Check if the manufacturer selection button was clicked
                    if self.manufacturer_button_rect.collidepoint(event.pos):
                        self.state = STATE_MANUFACTURER_SELECTION
                        self.message = "Select a manufacturer for your car"
                        self.message_timer = 180
                    
                    # Check if garage selection arrows were clicked
                    if hasattr(self, 'garage_left_arrow_rect') and self.garage_left_arrow_rect.collidepoint(event.pos):
                        # Switch to previous engineer car
                        if len(self.engineer_car_indices) > 0:
                            # Find current index in engineer_car_indices
                            current_idx = self.engineer_car_indices.index(self.selected_car_index) \
                                if self.selected_car_index in self.engineer_car_indices else 0
                            # Get previous engineer car index
                            next_idx = (current_idx - 1) % len(self.engineer_car_indices)
                            self.selected_car_index = self.engineer_car_indices[next_idx]
                            self.message = f"Selected {self.cars[self.selected_car_index].name}"
                            self.message_timer = 120
                            
                    if hasattr(self, 'garage_right_arrow_rect') and self.garage_right_arrow_rect.collidepoint(event.pos):
                        # Switch to next engineer car
                        if len(self.engineer_car_indices) > 0:
                            # Find current index in engineer_car_indices
                            current_idx = self.engineer_car_indices.index(self.selected_car_index) \
                                if self.selected_car_index in self.engineer_car_indices else 0
                            # Get next engineer car index
                            next_idx = (current_idx + 1) % len(self.engineer_car_indices)
                            self.selected_car_index = self.engineer_car_indices[next_idx]
                            self.message = f"Selected {self.cars[self.selected_car_index].name}"
                            self.message_timer = 120
                
                elif self.state == STATE_MANUFACTURER_SELECTION:
                    # Check if Back to Garage button was clicked
                    if self.back_button_rect.collidepoint(event.pos):
                        try:
                            # Before returning to customization screen, select the current manufacturer
                            if hasattr(self, 'ui'):
                                # Get the currently displayed manufacturer
                                selected_manufacturer = self.ui.manufacturer_ui.get_selected_manufacturer()
                                
                                # Save the current car's setup and upgrades before switching
                                self.save_current_player_stats()
                                
                                # Get the selected car and its garage name
                                car = self.cars[self.selected_car_index]
                                new_manufacturer = selected_manufacturer["name"]
                                garage_name = car.name
                                
                                # Update only the currently selected car with the new manufacturer
                                car.update_manufacturer(new_manufacturer)
                                
                                # Update team manufacturer in game if first car is selected
                                if car.name == "Team Alpha":
                                    self.player_team_manufacturer = new_manufacturer
                                
                                # Import functions for garage data
                                from player_data import get_player_garage, update_player_garage, get_car_upgrades
                                
                                # Load the existing garage data for this car
                                garage_data = get_player_garage(self.player_name, car.name)
                                
                                # Update the manufacturer
                                garage_data["manufacturer"] = new_manufacturer
                                
                                # Make sure we have upgrades for this manufacturer in this garage
                                if "cars" not in garage_data:
                                    garage_data["cars"] = {}
                                
                                if new_manufacturer not in garage_data["cars"]:
                                    garage_data["cars"][new_manufacturer] = {
                                        "upgrades": {"engine": 0, "tires": 0, "aero": 0}
                                    }
                                
                                # Get the car-specific upgrades for the new manufacturer
                                car_upgrades = get_car_upgrades(self.player_name, garage_name, new_manufacturer)
                                
                                # Update our in-memory car_upgrades dictionary
                                if garage_name not in self.car_upgrades:
                                    self.car_upgrades[garage_name] = {}
                                
                                self.car_upgrades[garage_name] = car_upgrades
                                
                                # Save the updated garage data
                                update_player_garage(
                                    self.player_name,
                                    car.name,
                                    new_manufacturer,
                                    garage_data["setup"],
                                    car_upgrades
                                )
                                
                                # Update car performance based on new manufacturer and upgrades
                                car.update_performance_from_setup()
                            
                            # Return to customization screen
                            self.state = STATE_CUSTOMIZATION
                            self.message = f"Selected {selected_manufacturer['name']} for {car.name}"
                            self.message_timer = 120
                        except Exception as e:
                            print(f"Error: {e}")
                            # Return to customization screen even if there was an error
                            self.state = STATE_CUSTOMIZATION
                            self.message = "Error selecting manufacturer, using default settings"
                            self.message_timer = 180
                    
                    # Check if left arrow was clicked
                    if self.left_arrow_rect.collidepoint(event.pos):
                        # Use the global UI instance
                        if hasattr(self, 'ui'):
                            self.ui.manufacturer_ui.rotate_carousel_left()
                    
                    # Check if right arrow was clicked
                    if self.right_arrow_rect.collidepoint(event.pos):
                        # Use the global UI instance
                        if hasattr(self, 'ui'):
                            self.ui.manufacturer_ui.rotate_carousel_right()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == STATE_RACING:
                        self.state = STATE_PAUSE
                        self.message = "Game Paused!"
                        self.message_timer = 180
                    elif self.state == STATE_PAUSE:
                        self.state = STATE_RACING
                        self.message = "Race resumed!"
                        self.message_timer = 180
                    
                        
                # Handle Escape key to return to customization screen from racing
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_RACE_END:
                        # Go to customization screen instead of start screen
                        self.reset_race()
                        self.state = STATE_CUSTOMIZATION
                    elif self.state == STATE_CUSTOMIZATION:
                        # Return to start screen from customization
                        self.state = STATE_START_SCREEN
                    elif self.state == STATE_RACING or self.state == STATE_PAUSE:
                        # Cancel race and return to customization
                        self.reset_race()
                        self.state = STATE_CUSTOMIZATION
                        self.message = "Race canceled!"
                        self.message_timer = 180
                    elif self.state == STATE_MANUFACTURER_SELECTION:
                        # Return to customization screen from manufacturer selection
                        self.state = STATE_CUSTOMIZATION
                        self.message = "Back to garage"
                        self.message_timer = 120
                
                # Toggle waypoints visibility with W key
                if event.key == pygame.K_w and self.state != STATE_START_SCREEN and self.state != STATE_RACE_END and self.state != STATE_CUSTOMIZATION:
                    self.show_waypoints = not self.show_waypoints
                    if self.show_waypoints:
                        self.message = "Waypoints visible"
                    else:
                        self.message = "Waypoints hidden"
                    self.message_timer = 120
                
                # Select different engineer car with arrow keys (works in both race and customization screens)
                if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    if self.state == STATE_MANUFACTURER_SELECTION:
                        # Rotate carousel left in manufacturer selection
                        if hasattr(self, 'ui'):
                            self.ui.manufacturer_ui.rotate_carousel_left()
                    else:
                        # Cycle through only the engineer cars
                        if len(self.engineer_car_indices) > 0:
                            # Find current index in engineer_car_indices
                            current_idx = self.engineer_car_indices.index(self.selected_car_index) \
                                if self.selected_car_index in self.engineer_car_indices else 0
                            # Get previous engineer car index
                            next_idx = (current_idx - 1) % len(self.engineer_car_indices)
                            self.selected_car_index = self.engineer_car_indices[next_idx]
                            self.message = f"Selected {self.cars[self.selected_car_index].name}"
                            self.message_timer = 120
                    
                if event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    if self.state == STATE_MANUFACTURER_SELECTION:
                        # Rotate carousel right in manufacturer selection
                        if hasattr(self, 'ui'):
                            self.ui.manufacturer_ui.rotate_carousel_right()
                    else:
                        # Cycle through only the engineer cars
                        if len(self.engineer_car_indices) > 0:
                            # Find current index in engineer_car_indices
                            current_idx = self.engineer_car_indices.index(self.selected_car_index) \
                                if self.selected_car_index in self.engineer_car_indices else 0
                            # Get next engineer car index
                            next_idx = (current_idx + 1) % len(self.engineer_car_indices)
                            self.selected_car_index = self.engineer_car_indices[next_idx]
                            self.message = f"Selected {self.cars[self.selected_car_index].name}"
                            self.message_timer = 120
                
                # Handle return/enter key to select manufacturer and return to customization screen
                if event.key == pygame.K_RETURN and self.state == STATE_MANUFACTURER_SELECTION:
                    try:
                        # Get selected manufacturer from UI
                        if hasattr(self, 'ui'):
                            selected_manufacturer = self.ui.manufacturer_ui.get_selected_manufacturer()
                            
                            # Save the current setup before switching manufacturer
                            self.save_current_player_stats()
                            
                            # Get the selected car and apply the new manufacturer
                            car = self.cars[self.selected_car_index]
                            new_manufacturer = selected_manufacturer["name"]
                            garage_name = car.name
                            car.update_manufacturer(new_manufacturer)
                            
                            # Update team manufacturer in game if the first car is selected
                            if car.name == "Team Alpha":
                                self.player_team_manufacturer = new_manufacturer
                                
                            # Import functions for garage data
                            from player_data import get_player_garage, update_player_garage, get_car_upgrades
                            
                            # Load the existing garage data for this car
                            garage_data = get_player_garage(self.player_name, car.name)
                            
                            # Update the manufacturer in the garage data
                            garage_data["manufacturer"] = new_manufacturer
                            
                            # Make sure we have upgrades for this manufacturer in this garage
                            if "cars" not in garage_data:
                                garage_data["cars"] = {}
                            
                            if new_manufacturer not in garage_data["cars"]:
                                garage_data["cars"][new_manufacturer] = {
                                    "upgrades": {"engine": 0, "tires": 0, "aero": 0}
                                }
                            
                            # Get the car-specific upgrades for the new manufacturer
                            car_upgrades = get_car_upgrades(self.player_name, garage_name, new_manufacturer)
                            
                            # Update our in-memory car_upgrades dictionary
                            if garage_name not in self.car_upgrades:
                                self.car_upgrades[garage_name] = {}
                            
                            self.car_upgrades[garage_name] = car_upgrades
                            
                            # Save the updated garage data
                            update_player_garage(
                                self.player_name,
                                car.name,
                                new_manufacturer,
                                garage_data["setup"],
                                car_upgrades
                            )
                            
                            # Update car performance based on the new manufacturer and upgrades
                            car.update_performance_from_setup()
                            
                            # Return to customization screen
                            self.state = STATE_CUSTOMIZATION
                            self.message = f"Selected {selected_manufacturer['name']} for {car.name}"
                            self.message_timer = 180
                        
                    except Exception as e:
                        print(f"Error: {e}")
                        # Return to customization screen even if there was an error
                        self.state = STATE_CUSTOMIZATION
                        self.message = "Error selecting manufacturer, using default settings"
                        self.message_timer = 180
                    
                # Engineer commands
                if event.key == pygame.K_p and self.state == STATE_RACING:
                    selected_car = self.cars[self.selected_car_index]
                    response = selected_car.toggle_push_mode()
                    self.message = response
                    self.message_timer = 180
            
            # Handle text input for new player name
            if self.adding_new_player and self.input_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        from player_data import add_player
                        if self.new_player_name.strip():
                            add_player(self.new_player_name)
                            self.players = load_players()
                            self.available_player_names = list(self.players.keys())
                            self.select_player(self.new_player_name)
                            self.adding_new_player = False
                            self.new_player_name = ""
                            self.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.new_player_name = self.new_player_name[:-1]
                    else:
                        # Limit name length to prevent UI issues
                        if len(self.new_player_name) < 20:
                            self.new_player_name += event.unicode
            
            # Handle mouse clicks for player selection, adding, and deletion
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                if self.state == STATE_START_SCREEN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.start_button_rect.collidepoint(mouse_pos):
                        self.state = STATE_CUSTOMIZATION
                        self.message = "Select your car and manufacturer"
                        self.message_timer = 180
                    
                    # Check if clicked on Add Player button
                    if self.add_player_button_rect.collidepoint(mouse_pos):
                        self.adding_new_player = True
                        self.input_active = True
                    
                    # Check if clicked on player selection
                    for i, button_rect in enumerate(self.player_buttons):
                        if i < len(self.available_player_names) and button_rect.collidepoint(mouse_pos):
                            self.select_player(self.available_player_names[i])
                            self.selected_player_index = i
                    
                    # Check if clicked on delete button
                    for i, button_rect in enumerate(self.delete_buttons):
                        if i < len(self.available_player_names) and button_rect.collidepoint(mouse_pos):
                            from player_data import delete_player
                            delete_player(self.available_player_names[i])
                            self.players = load_players()
                            self.available_player_names = list(self.players.keys())
                            if not self.available_player_names:
                                from player_data import add_player
                                add_player("Team Alpha Racing")
                                self.players = load_players()
                                self.available_player_names = list(self.players.keys())
                            self.select_player(self.available_player_names[0])
                            self.selected_player_index = 0
    
    # Keep the original handle_events for backward compatibility but make it call process_events
    def handle_events(self):
        """Legacy method - now just passes pygame events to process_events"""
        self.process_events(pygame.event.get())
    
    def update(self):
        if self.state == STATE_RACING:
            # Update race time
            self.race_time += 1
            
            # Update all cars
            for car in self.cars:
                car.update(1)
                
            # Update message timer
            if self.message_timer > 0:
                self.message_timer -= 1

            # Update camera position to follow the selected car
            selected_car = self.cars[self.selected_car_index]
            target_x = selected_car.x - SCREEN_WIDTH // 2
            target_y = selected_car.y - SCREEN_HEIGHT // 2
            self.camera_x += (target_x - self.camera_x) * CAMERA_SMOOTHNESS
            self.camera_y += (target_y - self.camera_y) * CAMERA_SMOOTHNESS
            
            # Update race positions
            self.update_race_positions()
        
        # At the end of update, save player stats if needed
        if self.state == STATE_RACE_END:
            self.save_current_player_stats()

    def update_race_positions(self):
        """Calculate current race positions based on laps completed and distance to next waypoint"""
        # Create a list of (car_index, score) tuples where higher score = better position
        positions_data = []
        
        total_waypoints = len(self.track.waypoints)
        
        for i, car in enumerate(self.cars):
            # Get the current target waypoint coordinates
            target_waypoint = self.track.waypoints[car.current_waypoint]
            waypoint_x = target_waypoint[0] * self.track.tile_size + self.track.tile_size // 2
            waypoint_y = target_waypoint[1] * self.track.tile_size + self.track.tile_size // 2
            
            # Calculate distance to current waypoint
            dx = waypoint_x - car.x
            dy = waypoint_y - car.y
            distance_to_waypoint = math.sqrt(dx**2 + dy**2)
            
            # Normalize the distance (0 = far, 1 = close)
            max_distance = self.track.tile_size * 4  # Max expected distance
            normalized_distance = max(0, 1 - (distance_to_waypoint / max_distance))
            
            # Create a comprehensive score:
            # - Primary: Current lap (biggest factor)
            # - Secondary: Current waypoint (fraction through current lap)
            # - Tertiary: Distance to next waypoint (small adjustment)
            waypoint_progress = car.current_waypoint / total_waypoints
            distance_factor = normalized_distance / (total_waypoints * 2)  # Make distance less significant than waypoint
            
            # Final score formula - higher is better
            score = car.laps + waypoint_progress + distance_factor
            
            positions_data.append((i, score))
        
        # Sort by score in descending order (higher score = better position)
        positions_data.sort(key=lambda x: x[1], reverse=True)
        
        # Extract just the car indices in order of position
        self.race_positions = [idx for idx, _ in positions_data]
        
        # Check if any car has completed all laps
        for car in self.cars:
            if car.laps >= self.MAX_LAPS and not self.race_finished:
                self.race_finished = True
                self.final_positions = self.race_positions.copy()
                self.state = STATE_RACE_END
                
                # Calculate rewards after race completion
                self.calculate_race_rewards()
                break

    def calculate_race_rewards(self):
        """Calculate points and experience earned based on race positions"""
        # Reset counters for this race
        self.last_race_points_earned = 0
        self.last_race_xp_earned = 0
        
        # Points scale by position - first place gets significantly more
        points_by_position = {
            1: 250, 
            2: 180, 
            3: 150, 
            4: 100, 
            5: 50
        }
        
        # Experience scale by position
        # Experience is harder to earn than points
        xp_by_position = {
            1: 15,
            2: 10, 
            3: 8,
            4: 5,
            5: 2
        }
        
        # Check each engineer car's position and award points and XP
        for car_idx in self.engineer_car_indices:
            if car_idx in self.final_positions:
                position = self.final_positions.index(car_idx) + 1
                
                # Award points based on position
                points = points_by_position.get(position, 0)
                self.last_race_points_earned += points
                self.player_points += points
                
                # Award experience based on position
                xp = xp_by_position.get(position, 0)
                self.last_race_xp_earned += xp
                self.player_team_rating += xp
                
                # Track wins
                if position == 1:
                    self.player_races_won += 1
        
    def reset_race(self):
        """Reset race state to prepare for a new race"""
        # Reset race time
        self.race_time = 0
        
        # Reset race positions
        self.race_positions = []
        self.final_positions = []
        self.race_finished = False
        
        # Reset all cars to starting position at waypoint 0
        # Get all spawn positions
        spawn_positions = self.track.get_all_spawn_positions()
        
        for i, car in enumerate(self.cars):
            # Reset position to first spawn position based on index
            if i < len(spawn_positions):
                car.x, car.y = spawn_positions[i]
            else:
                # If more cars than spawn points, use the first spawn point
                car.x, car.y = spawn_positions[0]
            
            # Add small random offset to avoid collision at start
            car.x += random.randint(-10, 10)
            car.y += random.randint(-10, 10)
            
            # Reset direction
            car.initialize_car_direction()
            
            # Reset racing properties
            car.current_waypoint = 0
            car.laps = 0
            car.speed = 0
            car.crashed = False
            car.recovery_timer = 0
            car.push_mode = False
            car.push_remaining = 0
            
            # Make sure the car has a reference to the game
            if not hasattr(car, 'game'):
                car.game = self
                
            # Make sure is_engineer_car is set properly
            if car.name == "Team Alpha" or car.name == "Team Omega":
                car.is_engineer_car = True
                car.can_push = True
            else:
                car.is_engineer_car = False
                car.can_push = False
            
            # Keep track of best lap from previous race
            # car.lap_times = []  # Uncomment to reset lap history
            # car.best_lap = None  # Uncomment to reset best lap
            
            # Reset lap timing
            car.last_lap_time = 0
            car.lap_start_time = pygame.time.get_ticks()
            
        # Reset camera position
        self.camera_x = 0
        self.camera_y = 0
        
        # Display message
        self.message = "Race reset! Press SPACE to start a new race."
        self.message_timer = 180