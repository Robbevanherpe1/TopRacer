import pygame
import math
import random
from constants import *  # Import all constants including STATE_RACING, STATE_RACE_END, SCREEN_WIDTH, etc.


class RaceGame:
    """Race component for handling race-related functionality"""
    
    def __init__(self, game):
        self.game = game
    
    def update(self):
        """Update race state"""
        if self.game.state == STATE_RACING:
            # Update race time
            self.game.race_time += 1
            
            # Update all cars
            for car in self.game.cars:
                car.update(1)
                
            # Update message timer
            if self.game.message_timer > 0:
                self.game.message_timer -= 1

            # Update camera position to follow the selected car
            selected_car = self.game.cars[self.game.selected_car_index]
            target_x = selected_car.x - SCREEN_WIDTH // 2
            target_y = selected_car.y - SCREEN_HEIGHT // 2
            self.game.camera_x += (target_x - self.game.camera_x) * CAMERA_SMOOTHNESS
            self.game.camera_y += (target_y - self.game.camera_y) * CAMERA_SMOOTHNESS
            
            # Update race positions
            self.update_race_positions()
        
        # At the end of update, save player stats if needed
        if self.game.state == STATE_RACE_END:
            self.game.save_current_player_stats()
    
    def update_race_positions(self):
        """Calculate current race positions based on laps completed and distance to next waypoint"""
        # Create a list of (car_index, score) tuples where higher score = better position
        positions_data = []
        
        total_waypoints = len(self.game.track.waypoints)
        
        for i, car in enumerate(self.game.cars):
            # Get the current target waypoint coordinates
            target_waypoint = self.game.track.waypoints[car.current_waypoint]
            waypoint_x = target_waypoint[0] * self.game.track.tile_size + self.game.track.tile_size // 2
            waypoint_y = target_waypoint[1] * self.game.track.tile_size + self.game.track.tile_size // 2
            
            # Calculate distance to current waypoint
            dx = waypoint_x - car.x
            dy = waypoint_y - car.y
            distance_to_waypoint = math.sqrt(dx**2 + dy**2)
            
            # Normalize the distance (0 = far, 1 = close)
            max_distance = self.game.track.tile_size * 4  # Max expected distance
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
        self.game.race_positions = [idx for idx, _ in positions_data]
        
        # Check if any car has completed all laps
        for car in self.game.cars:
            if car.laps >= self.game.MAX_LAPS and not self.game.race_finished:
                self.game.race_finished = True
                self.game.final_positions = self.game.race_positions.copy()
                self.game.state = STATE_RACE_END
                
                # Calculate rewards after race completion
                self.calculate_race_rewards()
                break
    
    def calculate_race_rewards(self):
        """Calculate points and experience earned based on race positions"""
        # Reset counters for this race
        self.game.last_race_points_earned = 0
        self.game.last_race_xp_earned = 0
        
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
        for car_idx in self.game.engineer_car_indices:
            if car_idx in self.game.final_positions:
                position = self.game.final_positions.index(car_idx) + 1
                
                # Award points based on position
                points = points_by_position.get(position, 0)
                self.game.last_race_points_earned += points
                self.game.player_points += points
                
                # Award experience based on position
                xp = xp_by_position.get(position, 0)
                self.game.last_race_xp_earned += xp
                self.game.player_team_rating += xp
                
                # Track wins
                if position == 1:
                    self.game.player_races_won += 1
    
    def reset_race(self):
        """Reset race state to prepare for a new race"""
        # Reset race time
        self.game.race_time = 0
        
        # Reset race positions
        self.game.race_positions = []
        self.game.final_positions = []
        self.game.race_finished = False
        
        # Reset all cars to starting position at waypoint 0
        # Get all spawn positions
        spawn_positions = self.game.track.get_all_spawn_positions()
        
        for i, car in enumerate(self.game.cars):
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
                car.game = self.game
                
            # Make sure is_engineer_car is set properly
            if car.name == "Team Alpha" or car.name == "Team Omega":
                car.is_engineer_car = True
                car.can_push = True
            else:
                car.is_engineer_car = False
                car.can_push = False
            
            # Reset lap timing
            car.last_lap_time = 0
            car.lap_start_time = pygame.time.get_ticks()
        
        # Reset camera position
        self.game.camera_x = 0
        self.game.camera_y = 0
        
        # Display message
        self.game.message = "Race reset! Press SPACE to start a new race."
        self.game.message_timer = 180