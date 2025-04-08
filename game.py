import pygame
import random
import math
from track import Track
from car import Car
from constants import *

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
        
        # Player stats - enhanced with proper rewards system
        self.player_points = 0
        self.player_team_rating = 0
        self.player_races_won = 0
        self.player_username = "Player1"
        
        # New stats for last race performance
        self.last_race_points_earned = 0
        self.last_race_xp_earned = 0
        
        # Permanent upgrade levels (0-10)
        self.engine_upgrade_level = 0
        self.tires_upgrade_level = 0
        self.aero_upgrade_level = 0
        
        # Upgrade costs - increases with each level
        self.base_upgrade_cost = 100
        self.upgrade_buttons = {}
        
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
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == STATE_START_SCREEN:
                        # Now go to customization screen instead of directly to racing
                        self.state = STATE_CUSTOMIZATION
                        self.message = "Customize your car before racing!"
                        self.message_timer = 180
                    elif self.state == STATE_RACING:
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
                    
                # Engineer commands
                if event.key == pygame.K_p and self.state == STATE_RACING:
                    selected_car = self.cars[self.selected_car_index]
                    response = selected_car.toggle_push_mode()
                    self.message = response
                    self.message_timer = 180
    
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
        for car in self.cars:
            # Reset position to first waypoint (waypoint 0) instead of finish line
            car.x, car.y = self.track.get_waypoint_position(0)
            
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