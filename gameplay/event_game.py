import pygame
from constants import *
from player_data import add_player, delete_player, load_players, get_player_garage, update_player_garage, get_car_upgrades


class EventGame:
    """Event handling component for processing game events"""
    
    def __init__(self, game):
        self.game = game
    
    def handle_events(self):
        """Legacy method - now just passes pygame events to process_events"""
        self.process_events(pygame.event.get())
    
    def process_events(self, events):
        """Process pygame events passed from the main loop"""
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
                
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                global SCREEN_WIDTH, SCREEN_HEIGHT
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                self.game.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
            # Handle mouse clicks for buttons
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse click
                self._handle_mouse_click(event)
            
            if event.type == pygame.KEYDOWN:
                self._handle_key_press(event)
            
            # Handle text input for new player name
            if self.game.adding_new_player and self.game.input_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.game.new_player_name.strip():
                            add_player(self.game.new_player_name)
                            self.game.players = load_players()
                            self.game.available_player_names = list(self.game.players.keys())
                            self.game.select_player(self.game.new_player_name)
                            self.game.adding_new_player = False
                            self.game.new_player_name = ""
                            self.game.input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.game.new_player_name = self.game.new_player_name[:-1]
                    else:
                        # Limit name length to prevent UI issues
                        if len(self.game.new_player_name) < 20:
                            self.game.new_player_name += event.unicode
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events based on game state"""
        if self.game.state == STATE_RACE_END:
            # Check if Return to Customization button was clicked
            if self.game.menu_button_rect.collidepoint(event.pos):
                # Reset the race and go to customization screen
                self.game.reset_race()
                self.game.state = STATE_CUSTOMIZATION
                self.game.message = "Customize your cars for the next race"
                self.game.message_timer = 180
                
        elif self.game.state == STATE_CUSTOMIZATION:
            # Check if Start Race button was clicked
            if self.game.start_race_button_rect.collidepoint(event.pos):
                # Check if BOTH engineer cars have balanced setup (sum of all values equals 25)
                all_balanced = True
                unbalanced_cars = []
                
                for car_idx in self.game.engineer_car_indices:
                    car = self.game.cars[car_idx]
                    total_balance = sum(car.setup.values())
                    if total_balance != 25:
                        all_balanced = False
                        unbalanced_cars.append(car.name)
                
                if all_balanced and hasattr(self.game, 'race_button_enabled') and self.game.race_button_enabled:
                    self.game.state = STATE_RACING
                    self.game.message = "Race started!"
                    self.game.message_timer = 180
                else:
                    self.game.message = f"All cars must have exactly 25 setup points to start! Check: {', '.join(unbalanced_cars)}" if unbalanced_cars else "Car setups must be balanced!"
                    self.game.message_timer = 180
            
            # Check if Menu button was clicked
            if hasattr(self.game, 'menu_button_rect') and self.game.menu_button_rect.collidepoint(event.pos):
                if hasattr(self.game, 'menu_button_enabled') and self.game.menu_button_enabled:
                    # Save current player stats before returning to start screen
                    self.game.save_current_player_stats()
                    # Return to start screen
                    self.game.state = STATE_START_SCREEN
                    self.game.message = "Returned to main menu"
                    self.game.message_timer = 180
            
            # Check if the manufacturer selection button was clicked
            if self.game.manufacturer_button_rect.collidepoint(event.pos):
                self.game.state = STATE_MANUFACTURER_SELECTION
                self.game.message = "Select a manufacturer for your car"
                self.game.message_timer = 180
            
            # Check if garage selection arrows were clicked
            if hasattr(self.game, 'garage_left_arrow_rect') and self.game.garage_left_arrow_rect.collidepoint(event.pos):
                # Switch to previous engineer car
                if len(self.game.engineer_car_indices) > 0:
                    # Find current index in engineer_car_indices
                    current_idx = self.game.engineer_car_indices.index(self.game.selected_car_index) \
                        if self.game.selected_car_index in self.game.engineer_car_indices else 0
                    # Get previous engineer car index
                    next_idx = (current_idx - 1) % len(self.game.engineer_car_indices)
                    self.game.selected_car_index = self.game.engineer_car_indices[next_idx]
                    self.game.message = f"Selected {self.game.cars[self.game.selected_car_index].name}"
                    self.game.message_timer = 120
                    
            if hasattr(self.game, 'garage_right_arrow_rect') and self.game.garage_right_arrow_rect.collidepoint(event.pos):
                # Switch to next engineer car
                if len(self.game.engineer_car_indices) > 0:
                    # Find current index in engineer_car_indices
                    current_idx = self.game.engineer_car_indices.index(self.game.selected_car_index) \
                        if self.game.selected_car_index in self.game.engineer_car_indices else 0
                    # Get next engineer car index
                    next_idx = (current_idx + 1) % len(self.game.engineer_car_indices)
                    self.game.selected_car_index = self.game.engineer_car_indices[next_idx]
                    self.game.message = f"Selected {self.game.cars[self.game.selected_car_index].name}"
                    self.game.message_timer = 120
                    
        elif self.game.state == STATE_MANUFACTURER_SELECTION:
            # Check if Back to Garage button was clicked
            if self.game.back_button_rect.collidepoint(event.pos):
                self._handle_manufacturer_selection()
            
            # Check if left arrow was clicked
            if self.game.left_arrow_rect.collidepoint(event.pos):
                # Use the global UI instance
                if hasattr(self.game, 'ui'):
                    self.game.ui.manufacturer_ui.rotate_carousel_left()
            
            # Check if right arrow was clicked
            if self.game.right_arrow_rect.collidepoint(event.pos):
                # Use the global UI instance
                if hasattr(self.game, 'ui'):
                    self.game.ui.manufacturer_ui.rotate_carousel_right()
                    
        elif self.game.state == STATE_START_SCREEN:
            mouse_pos = event.pos
            
            if self.game.start_button_rect.collidepoint(mouse_pos):
                self.game.state = STATE_CUSTOMIZATION
                self.game.message = "Select your car and manufacturer"
                self.game.message_timer = 180
            
            # Check if clicked on Add Player button
            if self.game.add_player_button_rect.collidepoint(mouse_pos):
                self.game.adding_new_player = True
                self.game.input_active = True
            
            # Check if clicked on player selection
            for i, button_rect in enumerate(self.game.player_buttons):
                if i < len(self.game.available_player_names) and button_rect.collidepoint(mouse_pos):
                    self.game.select_player(self.game.available_player_names[i])
                    self.game.selected_player_index = i
            
            # Check if clicked on delete button
            for i, button_rect in enumerate(self.game.delete_buttons):
                if i < len(self.game.available_player_names) and button_rect.collidepoint(mouse_pos):
                    delete_player(self.game.available_player_names[i])
                    self.game.players = load_players()
                    self.game.available_player_names = list(self.game.players.keys())
                    if not self.game.available_player_names:
                        add_player("Team Alpha Racing")
                        self.game.players = load_players()
                        self.game.available_player_names = list(self.game.players.keys())
                    self.game.select_player(self.game.available_player_names[0])
                    self.game.selected_player_index = 0
    
    def _handle_key_press(self, event):
        """Handle keyboard events"""
        if event.key == pygame.K_SPACE:
            if self.game.state == STATE_RACING:
                self.game.state = STATE_PAUSE
                self.game.message = "Game Paused!"
                self.game.message_timer = 180
            elif self.game.state == STATE_PAUSE:
                self.game.state = STATE_RACING
                self.game.message = "Race resumed!"
                self.game.message_timer = 180
            
        # Handle Escape key
        if event.key == pygame.K_ESCAPE:
            if self.game.state == STATE_RACE_END:
                # Go to customization screen instead of start screen
                self.game.reset_race()
                self.game.state = STATE_CUSTOMIZATION
            elif self.game.state == STATE_CUSTOMIZATION:
                # Return to start screen from customization
                self.game.state = STATE_START_SCREEN
            elif self.game.state == STATE_RACING or self.game.state == STATE_PAUSE:
                # Cancel race and return to customization
                self.game.reset_race()
                self.game.state = STATE_CUSTOMIZATION
                self.game.message = "Race canceled!"
                self.game.message_timer = 180
            elif self.game.state == STATE_MANUFACTURER_SELECTION:
                # Return to customization screen from manufacturer selection
                self.game.state = STATE_CUSTOMIZATION
                self.game.message = "Back to garage"
                self.game.message_timer = 120
        
        # Toggle waypoints visibility with W key
        if event.key == pygame.K_w and self.game.state != STATE_START_SCREEN and self.game.state != STATE_RACE_END and self.game.state != STATE_CUSTOMIZATION:
            self.game.show_waypoints = not self.game.show_waypoints
            if self.game.show_waypoints:
                self.game.message = "Waypoints visible"
            else:
                self.game.message = "Waypoints hidden"
            self.game.message_timer = 120
        
        # Select different engineer car with arrow keys
        if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
            self._handle_left_arrow()
            
        if event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
            self._handle_right_arrow()
            
        # Handle return key to select manufacturer
        if event.key == pygame.K_RETURN and self.game.state == STATE_MANUFACTURER_SELECTION:
            self._handle_manufacturer_selection()
            
        # Engineer commands
        if event.key == pygame.K_p and self.game.state == STATE_RACING:
            selected_car = self.game.cars[self.game.selected_car_index]
            response = selected_car.toggle_push_mode()
            self.game.message = response
            self.game.message_timer = 180
    
    def _handle_left_arrow(self):
        """Handle left arrow key based on game state"""
        if self.game.state == STATE_MANUFACTURER_SELECTION:
            # Rotate carousel left in manufacturer selection
            if hasattr(self.game, 'ui'):
                self.game.ui.manufacturer_ui.rotate_carousel_left()
        else:
            # Cycle through only the engineer cars
            if len(self.game.engineer_car_indices) > 0:
                # Find current index in engineer_car_indices
                current_idx = self.game.engineer_car_indices.index(self.game.selected_car_index) \
                    if self.game.selected_car_index in self.game.engineer_car_indices else 0
                # Get previous engineer car index
                next_idx = (current_idx - 1) % len(self.game.engineer_car_indices)
                self.game.selected_car_index = self.game.engineer_car_indices[next_idx]
                self.game.message = f"Selected {self.game.cars[self.game.selected_car_index].name}"
                self.game.message_timer = 120
    
    def _handle_right_arrow(self):
        """Handle right arrow key based on game state"""
        if self.game.state == STATE_MANUFACTURER_SELECTION:
            # Rotate carousel right in manufacturer selection
            if hasattr(self.game, 'ui'):
                self.game.ui.manufacturer_ui.rotate_carousel_right()
        else:
            # Cycle through only the engineer cars
            if len(self.game.engineer_car_indices) > 0:
                # Find current index in engineer_car_indices
                current_idx = self.game.engineer_car_indices.index(self.game.selected_car_index) \
                    if self.game.selected_car_index in self.game.engineer_car_indices else 0
                # Get next engineer car index
                next_idx = (current_idx + 1) % len(self.game.engineer_car_indices)
                self.game.selected_car_index = self.game.engineer_car_indices[next_idx]
                self.game.message = f"Selected {self.game.cars[self.game.selected_car_index].name}"
                self.game.message_timer = 120
    
    def _handle_manufacturer_selection(self):
        """Handle manufacturer selection confirmation"""
        try:
            # Get selected manufacturer from UI
            if hasattr(self.game, 'ui'):
                selected_manufacturer = self.game.ui.manufacturer_ui.get_selected_manufacturer()
                
                # Save the current setup before switching manufacturer
                self.game.save_current_player_stats()
                
                # Get the selected car and apply the new manufacturer
                car = self.game.cars[self.game.selected_car_index]
                new_manufacturer = selected_manufacturer["name"]
                garage_name = car.name
                car.update_manufacturer(new_manufacturer)
                
                # Update team manufacturer in game if the first car is selected
                if car.name == "Team Alpha":
                    self.game.player_team_manufacturer = new_manufacturer
                    
                # Load the existing garage data for this car
                garage_data = get_player_garage(self.game.player_name, car.name)
                
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
                car_upgrades = get_car_upgrades(self.game.player_name, garage_name, new_manufacturer)
                
                # Update our in-memory car_upgrades dictionary
                if garage_name not in self.game.car_upgrades:
                    self.game.car_upgrades[garage_name] = {}
                
                self.game.car_upgrades[garage_name] = car_upgrades
                
                # Save the updated garage data
                update_player_garage(
                    self.game.player_name,
                    car.name,
                    new_manufacturer,
                    garage_data["setup"],
                    car_upgrades
                )
                
                # Update car performance based on the new manufacturer and upgrades
                car.update_performance_from_setup()
                
                # Return to customization screen
                self.game.state = STATE_CUSTOMIZATION
                self.game.message = f"Selected {selected_manufacturer['name']} for {car.name}"
                self.game.message_timer = 180
            
        except Exception as e:
            print(f"Error: {e}")
            # Return to customization screen even if there was an error
            self.game.state = STATE_CUSTOMIZATION
            self.game.message = "Error selecting manufacturer, using default settings"
            self.game.message_timer = 180