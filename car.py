import pygame
import math
import random
from track import WALL

class Car:
    def __init__(self, track, position=None, color=(0, 0, 255), name="Player"):
        self.track = track
        self.name = name
        self.color = color
        
        # Set starting position
        if position:
            self.x, self.y = position
        else:
            self.x, self.y = track.get_start_position()
            
        # Set random starting position offsets for multiple cars
        self.x += random.randint(-10, 10)
        self.y += random.randint(-10, 10)
        
        # Car physics properties
        self.angle = 0  # Angle in degrees (0 = right, 90 = down)
        self.speed = 0
        self.max_speed = 5.0
        self.acceleration = 0.1
        self.turn_speed = 3.0
        
        # Car dimensions
        self.width = 20
        self.height = 10
        
        # Racing properties
        self.current_waypoint = 0
        self.laps = 0
        self.lap_times = []
        self.best_lap = None
        self.last_lap_time = 0
        self.lap_start_time = pygame.time.get_ticks()
        
        # Race engineer commands
        self.push_mode = False  # When true, car drives more aggressively
        self.push_remaining = 0  # Counts down when in push mode
        
        # Collision detection
        self.crashed = False
        self.recovery_timer = 0
        
    def toggle_push_mode(self):
        """Toggle 'push' mode for the car (race engineer command)"""
        if not self.push_mode:
            self.push_mode = True
            self.push_remaining = 600  # 10 seconds at 60fps
            return "Push mode activated! Driver will push for 10 seconds."
        else:
            return "Already in push mode!"
    
    def update(self, dt):
        """Update car position and handle AI driving"""
        if self.crashed:
            self.recovery_timer -= 1
            if self.recovery_timer <= 0:
                self.crashed = False
                # Move slightly backward to recover
                radians = math.radians(self.angle)
                self.x -= math.cos(radians) * 5
                self.y -= math.sin(radians) * 5
            return
        
        # Update push mode counter
        if self.push_mode:
            self.push_remaining -= 1
            if self.push_remaining <= 0:
                self.push_mode = False
        
        # AI driving logic
        target_waypoint = self.track.waypoints[self.current_waypoint]
        waypoint_x = target_waypoint[0] * self.track.tile_size + self.track.tile_size // 2
        waypoint_y = target_waypoint[1] * self.track.tile_size + self.track.tile_size // 2
        
        # Calculate angle to target waypoint
        dx = waypoint_x - self.x
        dy = waypoint_y - self.y
        target_angle = math.degrees(math.atan2(dy, dx))
        
        # Determine shortest angle to turn
        angle_diff = (target_angle - self.angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
            
        # Adjust steering based on the angle difference
        turn_amount = min(abs(angle_diff), self.turn_speed) * (1 if angle_diff > 0 else -1)
        self.angle = (self.angle + turn_amount) % 360
        
        # Determine if we should accelerate or brake
        distance_to_waypoint = math.sqrt(dx**2 + dy**2)
        
        # Change to next waypoint if close enough
        if distance_to_waypoint < 40:
            self.current_waypoint = (self.current_waypoint + 1) % len(self.track.waypoints)
            # Check if we've completed a lap
            if self.current_waypoint == 0:
                current_time = pygame.time.get_ticks()
                lap_time = (current_time - self.lap_start_time) / 1000  # Convert to seconds
                self.lap_times.append(lap_time)
                self.last_lap_time = lap_time
                if self.best_lap is None or lap_time < self.best_lap:
                    self.best_lap = lap_time
                self.lap_start_time = current_time
                self.laps += 1
        
        # Adjust speed based on conditions
        target_speed = self.max_speed
        
        # Slow down for turns (simple version)
        next_wp_idx = (self.current_waypoint + 1) % len(self.track.waypoints)
        next_waypoint = self.track.waypoints[next_wp_idx]
        next_wp_x = next_waypoint[0] * self.track.tile_size + self.track.tile_size // 2
        next_wp_y = next_waypoint[1] * self.track.tile_size + self.track.tile_size // 2
        
        # Calculate angle between current waypoint and next waypoint
        next_dx = next_wp_x - waypoint_x
        next_dy = next_wp_y - waypoint_y
        next_angle = math.degrees(math.atan2(next_dy, next_dx))
        
        # Calculate angle difference
        turn_angle = abs((next_angle - target_angle + 180) % 360 - 180)
        
        # Reduce speed for sharp turns
        if turn_angle > 45:
            target_speed *= 0.5
        elif turn_angle > 20:
            target_speed *= 0.7
        
        # Apply push mode if active
        if self.push_mode:
            target_speed *= 1.2
            
        # Accelerate or decelerate toward target speed
        if self.speed < target_speed:
            self.speed = min(self.speed + self.acceleration * (1.5 if self.push_mode else 1.0), target_speed)
        else:
            self.speed = max(self.speed - self.acceleration * 2, target_speed)
            
        # Convert angle to radians and update position
        radians = math.radians(self.angle)
        self.x += math.cos(radians) * self.speed
        self.y += math.sin(radians) * self.speed
        
        # Check for collision with walls
        self.check_collision()
        
    def check_collision(self):
        # Get the corners of the car for collision detection
        corners = self.get_corners()
        
        # Check if any corner is in a wall
        for corner in corners:
            cx, cy = corner
            # Convert to int before using as grid coordinates
            if self.track.get_tile_at(int(cx), int(cy)) == WALL:
                self.crashed = True
                self.recovery_timer = 30  # Half-second recovery at 60fps
                self.speed *= 0.5  # Slow down after crash
                return
    
    def get_corners(self):
        """Get the four corners of the car for collision detection"""
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        
        half_width = self.width / 2
        half_height = self.height / 2
        
        # Calculate rotated corners
        corners = []
        for xm, ym in [(-half_width, -half_height), 
                       (half_width, -half_height), 
                       (half_width, half_height), 
                       (-half_width, half_height)]:
            x = self.x + xm * cos_a - ym * sin_a
            y = self.y + xm * sin_a + ym * cos_a
            corners.append((x, y))
            
        return corners
        
    def draw(self, surface):
        # Draw car as a rotated rectangle (blue square for now)
        corners = self.get_corners()
        
        # Fill the car with its color
        pygame.draw.polygon(surface, self.color, corners)
        
        # Draw an outline for better visibility
        pygame.draw.polygon(surface, (0, 0, 0), corners, 1)
        
        # Draw a small line indicating the front of the car - ensure coordinates are integers
        front_x = int(self.x + math.cos(math.radians(self.angle)) * 15)
        front_y = int(self.y + math.sin(math.radians(self.angle)) * 15)
        pygame.draw.line(surface, (0, 0, 0), (int(self.x), int(self.y)), (front_x, front_y), 2)
        
    def get_status(self):
        """Return status text for display"""
        status = f"{self.name}: "
        if self.crashed:
            status += "CRASHED! "
        elif self.push_mode:
            status += "PUSHING! "
            
        status += f"Lap {self.laps + 1}"
        
        if self.last_lap_time > 0:
            status += f" | Last: {self.last_lap_time:.2f}s"
            
        if self.best_lap is not None:
            status += f" | Best: {self.best_lap:.2f}s"
            
        return status