import pygame
import math
import random
from track import WALL, TRACK

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
            
        # Set safer starting position offsets that avoid walls
        self.x += random.randint(-5, 5)
        self.y += random.randint(-5, 5)
        
        # Set initial angle to face the right direction towards first waypoint
        self.angle = 0  # Will be updated in initialize_car_direction()
        self.initialize_car_direction()
        
        # Car setup properties (values from 1-10)
        self.setup = {
            "Engine": 5,     # Affects top speed and acceleration
            "Tires": 5,      # Affects cornering and grip
            "Aerodynamics": 5, # Affects top speed and cornering at high speed
            "Handling": 5,   # Affects responsiveness in corners
            "Brakes": 5      # Affects braking efficiency
        }
        
        # Car physics properties - will be modified by setup
        self.base_max_speed = 6.0
        self.base_acceleration = 0.15
        self.base_turn_speed = 3.5
        self.base_braking = 2.0
        
        # Actual performance values (calculated from base + setup)
        self.max_speed = self.base_max_speed
        self.acceleration = self.base_acceleration
        self.turn_speed = self.base_turn_speed
        self.braking = self.base_braking
        
        # Initialize speed
        self.speed = 0
        
        # Calculate initial performance from setup
        self.update_performance_from_setup()
        
        # Car dimensions - made smaller
        self.width = 14  # Reduced from 20
        self.height = 7  # Reduced from 10
        
        # Racing properties
        self.current_waypoint = 0
        self.laps = 0
        self.lap_times = []
        self.best_lap = None
        self.last_lap_time = 0
        self.lap_start_time = pygame.time.get_ticks()
        
        # Race engineer commands
        self.push_mode = False
        self.push_remaining = 0
        self.can_push = True
        
        # Flag to identify cars controlled by the racing engineer
        self.is_engineer_car = False
        
        # Collision detection
        self.crashed = False
        self.recovery_timer = 0
        
        # Driver characteristics (adds some personality)
        self.skill_level = random.uniform(0.8, 1.2)  # Affects driving precision
        self.aggression = random.uniform(0.7, 1.3)   # Affects speed in corners
        
        if self.name == "Team Alpha":
            self.sprite = pygame.image.load("assets/ferrari.png").convert_alpha()
        else:
            self.sprite = None
        
    def initialize_car_direction(self):
        """Set initial car direction towards first waypoint"""
        # Get first waypoint
        target_waypoint = self.track.waypoints[0]
        waypoint_x = target_waypoint[0] * self.track.tile_size + self.track.tile_size // 2
        waypoint_y = target_waypoint[1] * self.track.tile_size + self.track.tile_size // 2
        
        # Calculate angle to target waypoint
        dx = waypoint_x - self.x
        dy = waypoint_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        
    def toggle_push_mode(self):
        """Toggle 'push' mode for the car (race engineer command)"""
        # Check if this car can use push mode
        if not self.can_push:
            return f"{self.name} can't use push mode!"
            
        if not self.push_mode:
            self.push_mode = True
            self.push_remaining = 600  # 10 seconds at 60fps
            return f"Push mode activated! {self.name} will push for 10 seconds."
        else:
            return f"{self.name} is already in push mode!"
    
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
        
        # AI driving logic - Get current target waypoint coordinates
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
            
        # Apply skill level and setup handling to steering precision
        # - Higher handling setup means better turn precision
        # - Higher tire setup means better grip in turns
        handling_effect = 0.8 + (self.setup["Handling"] / 10) * 0.4  # 0.8-1.2 range
        tire_effect = 0.8 + (self.setup["Tires"] / 10) * 0.4  # 0.8-1.2 range
        
        # Combine effects into a steering precision factor
        steering_factor = self.skill_level * ((handling_effect * 0.6) + (tire_effect * 0.4))
        if self.is_engineer_car:
            steering_factor *= 1.1  # Engineer cars are slightly more precise
            
        turn_amount = min(abs(angle_diff), self.turn_speed * steering_factor) * (1 if angle_diff > 0 else -1)
        self.angle = (self.angle + turn_amount) % 360
        
        # Determine distance to current waypoint
        distance_to_waypoint = math.sqrt(dx**2 + dy**2)
        
        # Improved waypoint transition - change to next waypoint when close enough
        # Better handling means tighter racing line
        waypoint_threshold = 35 * (1.1 - (handling_effect - 0.8) * 0.5)  # Threshold varies with handling
        if self.is_engineer_car:
            waypoint_threshold *= 0.9  # Engineer cars follow more precise line
        
        if distance_to_waypoint < waypoint_threshold:
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
        
        # Advanced racing line calculation - look ahead by 2 waypoints for better anticipation
        next_wp_idx = (self.current_waypoint + 1) % len(self.track.waypoints)
        next_waypoint = self.track.waypoints[next_wp_idx]
        next_wp_x = next_waypoint[0] * self.track.tile_size + self.track.tile_size // 2
        next_wp_y = next_waypoint[1] * self.track.tile_size + self.track.tile_size // 2
        
        # Also look at waypoint after next for better planning
        next2_wp_idx = (self.current_waypoint + 2) % len(self.track.waypoints)
        next2_waypoint = self.track.waypoints[next2_wp_idx]
        next2_wp_x = next2_waypoint[0] * self.track.tile_size + self.track.tile_size // 2
        next2_wp_y = next2_waypoint[1] * self.track.tile_size + self.track.tile_size // 2
        
        # Calculate angle between current waypoint and next waypoint
        next_dx = next_wp_x - waypoint_x
        next_dy = next_wp_y - waypoint_y
        next_angle = math.degrees(math.atan2(next_dy, next_dx))
        
        # Calculate angle for the turn after that
        next2_dx = next2_wp_x - next_wp_x
        next2_dy = next2_wp_y - next_wp_y
        next2_angle = math.degrees(math.atan2(next2_dy, next2_dx))
        
        # Calculate how sharp the upcoming turns are
        turn_angle = abs((next_angle - target_angle + 180) % 360 - 180)
        next_turn_angle = abs((next2_angle - next_angle + 180) % 360 - 180)
        
        # Determine maximum safe speed based on course conditions
        target_speed = self.max_speed
        
        # More sophisticated speed adjustment for turns
        # Look at both current turn and next turn to plan ahead
        current_turn_factor = 1.0
        next_turn_factor = 1.0
        
        # Factor for current turn
        if turn_angle > 70:
            current_turn_factor = 0.35
        elif turn_angle > 50:
            current_turn_factor = 0.5
        elif turn_angle > 30:
            current_turn_factor = 0.7
        elif turn_angle > 15:
            current_turn_factor = 0.85
        
        # Factor for next turn - less impact than current turn
        if next_turn_angle > 70:
            next_turn_factor = 0.6
        elif next_turn_angle > 50:
            next_turn_factor = 0.75
        elif next_turn_angle > 30:
            next_turn_factor = 0.85
        
        # Apply car setup factors to turn behavior:
        # - Better tires and handling allow maintaining more speed in corners
        # - Better aerodynamics helps with high-speed corners
        tire_corner_bonus = (self.setup["Tires"] - 5) * 0.015  # -0.06 to +0.075 range
        handling_corner_bonus = (self.setup["Handling"] - 5) * 0.01  # -0.04 to +0.05 range
        aero_corner_bonus = (self.setup["Aerodynamics"] - 5) * 0.008  # -0.032 to +0.04 range
        
        # Apply bonuses to turn factors (more effective in sharper turns)
        if turn_angle > 30:  # Only apply significant bonuses in actual corners
            current_turn_factor += tire_corner_bonus + handling_corner_bonus
            if self.speed > self.max_speed * 0.7:  # Aero only matters at higher speeds
                current_turn_factor += aero_corner_bonus
            
        # Apply similar bonuses to next turn factor
        if next_turn_angle > 30:
            next_turn_factor += tire_corner_bonus * 0.5 + handling_corner_bonus * 0.5
            if self.speed > self.max_speed * 0.7:
                next_turn_factor += aero_corner_bonus * 0.5
        
        # Ensure factors stay within reasonable bounds
        current_turn_factor = max(0.3, min(current_turn_factor, 1.0))
        next_turn_factor = max(0.5, min(next_turn_factor, 1.0))
        
        # Combine turn factors, with the current turn being more important
        combined_turn_factor = min(current_turn_factor, next_turn_factor * 1.2)
        
        # Apply driver aggression to speed through turns
        # Engineer cars can be more aggressive if push mode is active
        aggression_factor = self.aggression
        if self.is_engineer_car:
            aggression_factor += 0.1  # Engineer cars are slightly more aggressive
        
        # Calculate final target speed
        target_speed *= combined_turn_factor * aggression_factor
        
        # Apply push mode effect
        if self.push_mode:
            push_boost = 1.35  # Base push boost
            # Engine quality affects push effectiveness
            engine_push_bonus = (self.setup["Engine"] - 5) * 0.01  # -0.04 to +0.05 range
            push_boost += engine_push_bonus
            target_speed *= push_boost
            
        # Smoother acceleration/deceleration based on car setup
        if self.speed < target_speed:
            # Acceleration - affected by engine setup
            accel_factor = 1.0
            if self.push_mode:
                accel_factor = 1.8  # Push mode base acceleration boost
                
            # Apply engine quality to acceleration
            engine_accel_bonus = (self.setup["Engine"] - 5) * 0.04  # -0.16 to +0.2 range
            accel_factor += engine_accel_bonus
                
            if self.is_engineer_car:
                accel_factor *= 1.1  # Engineer cars have better acceleration
                
            self.speed = min(self.speed + self.acceleration * accel_factor, target_speed)
        else:
            # Braking - affected by brakes setup
            brake_factor = 2.0  # Base braking
            
            # Apply brakes quality to deceleration
            brakes_bonus = (self.setup["Brakes"] - 5) * 0.08  # -0.4 to +0.4 range
            brake_factor += brakes_bonus
            
            if self.is_engineer_car:
                brake_factor *= 1.1  # Engineer cars have slightly better braking
                
            self.speed = max(self.speed - self.acceleration * brake_factor, target_speed)
            
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
        
    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw car with camera offset applied"""
        # Calculate screen position with camera offset
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Get corners with camera offset applied
        corners = []
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        
        half_width = self.width / 2
        half_height = self.height / 2
        
        # Make engineer cars slightly larger for better visibility
        if self.is_engineer_car:
            half_width *= 1.2
            half_height *= 1.2
        
        # Calculate rotated corners with camera offset
        for xm, ym in [(-half_width, -half_height), 
                       (half_width, -half_height), 
                       (half_width, half_height), 
                       (-half_width, half_height)]:
            x = screen_x + xm * cos_a - ym * sin_a
            y = screen_y + xm * sin_a + ym * cos_a
            corners.append((x, y))
        
        if self.sprite:
            #scale down the sprite for better fit
            scaled_sprite = pygame.transform.scale(self.sprite, (45, 60))
            # Rotate sprite because the ferrari image points down by default
            rotated_sprite = pygame.transform.rotate(scaled_sprite, -self.angle + 90)
            rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
            surface.blit(rotated_sprite, rect)
        else:
            # Fill the car with its color
            pygame.draw.polygon(surface, self.color, corners)
        
        # Draw an outline for better visibility - thicker for engineer cars
        outline_thickness = 1 if self.is_engineer_car else 0
        pygame.draw.polygon(surface, (0, 0, 0), corners, outline_thickness)
        
        # Draw a small line indicating the front of the car - ensure coordinates are integers
        front_x = int(screen_x + math.cos(math.radians(self.angle)) * 15)
        front_y = int(screen_y + math.sin(math.radians(self.angle)) * 15)
        pygame.draw.line(surface, (0, 0, 0), (int(screen_x), int(screen_y)), (front_x, front_y), outline_thickness)
        
        # Add star indicators for engineer cars
        if self.is_engineer_car:
            # Draw a star above the car
            star_radius = 8
            star_y_offset = 20
            star_points = []
            
            # Calculate position for star (above the car)
            star_x = screen_x
            star_y = screen_y - star_y_offset
            
            # Create a 5-pointed star
            for i in range(5):
                # Outer point
                angle = math.radians(i * 72 - 90)  # Starting from the top point (-90 degrees)
                px = star_x + math.cos(angle) * star_radius
                py = star_y + math.sin(angle) * star_radius
                star_points.append((px, py))
                
                # Inner point
                angle = math.radians(i * 72 + 36 - 90)  # +36 degrees for inner points
                px = star_x + math.cos(angle) * (star_radius * 0.4)  # Inner radius is 40% of outer
                py = star_y + math.sin(angle) * (star_radius * 0.4)
                star_points.append((px, py))
            
            # Draw the star in bright yellow
            pygame.draw.polygon(surface, (255, 255, 0), star_points)
            pygame.draw.polygon(surface, (0, 0, 0), star_points, 1)
        
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
        
        # Show push capability
        if not self.can_push:
            status += " [NO PUSH]"
            
        return status

    def update_performance_from_setup(self):
        """Calculate car performance values based on setup"""
        # Engine affects top speed and acceleration
        engine_factor = 0.8 + (self.setup["Engine"] / 10) * 0.4  # 0.8-1.2 range
        
        # Tires affect cornering grip
        tires_factor = 0.8 + (self.setup["Tires"] / 10) * 0.4  # 0.8-1.2 range
        
        # Aerodynamics affect top speed and high-speed cornering
        aero_factor = 0.8 + (self.setup["Aerodynamics"] / 10) * 0.4  # 0.8-1.2 range
        
        # Handling affects turn responsiveness
        handling_factor = 0.8 + (self.setup["Handling"] / 10) * 0.4  # 0.8-1.2 range
        
        # Brakes affect braking efficiency
        brakes_factor = 0.8 + (self.setup["Brakes"] / 10) * 0.4  # 0.8-1.2 range
        
        # Calculate performance values
        self.max_speed = self.base_max_speed * ((engine_factor * 0.7) + (aero_factor * 0.3))
        self.acceleration = self.base_acceleration * engine_factor
        self.turn_speed = self.base_turn_speed * ((handling_factor * 0.6) + (tires_factor * 0.4))
        self.braking = self.base_braking * brakes_factor
        
    def set_random_setup(self):
        """Generate random setup values for AI cars"""
        for key in self.setup:
            self.setup[key] = random.randint(3, 8)  # Random values between 3-8
        self.update_performance_from_setup()
        
    def adjust_setup_balanced(self, key, new_value):
        """
        Adjust car setup while maintaining balance.
        When a value is increased above 5, other values are decreased proportionally.
        When a value is decreased below 5, other values are increased proportionally.
        The total sum of all setup values must remain 25 (5 stats × baseline value of 5)
        """
        # Get current value and calculate change
        old_value = self.setup[key]
        value_change = new_value - old_value
        
        # If no change, nothing to do
        if value_change == 0:
            return
        
        # Set the new value first
        self.setup[key] = new_value
        
        # Calculate how much we need to distribute to/from other stats
        points_to_distribute = -value_change  # negative because we're balancing
        
        # Get list of other keys that can be adjusted (all except the one being changed)
        other_keys = [k for k in self.setup.keys() if k != key]
        
        # Count how many adjustable keys we have (those not already at min or max)
        if points_to_distribute > 0:  # We need to increase other stats
            adjustable_keys = [k for k in other_keys if self.setup[k] < 10]
        else:  # We need to decrease other stats
            adjustable_keys = [k for k in other_keys if self.setup[k] > 1]
        
        # If no adjustable keys, revert the change
        if not adjustable_keys:
            self.setup[key] = old_value
            return
        
        # Calculate how many points to distribute to each stat
        points_per_key = points_to_distribute / len(adjustable_keys)
        
        # Apply distribution, ensuring no stat goes below 1 or above 10
        remaining_points = points_to_distribute
        for adjust_key in adjustable_keys:
            # Calculate new value with proportional adjustment
            if points_per_key > 0:  # Increasing other stats
                # How much can this stat increase?
                max_increase = 10 - self.setup[adjust_key]
                adjustment = min(points_per_key, max_increase)
            else:  # Decreasing other stats
                # How much can this stat decrease?
                max_decrease = self.setup[adjust_key] - 1
                adjustment = max(points_per_key, -max_decrease)
            
            # Apply the adjustment
            self.setup[adjust_key] += adjustment
            remaining_points -= adjustment
        
        # If we still have points to distribute (due to min/max limits),
        # try to distribute them among remaining adjustable keys
        if abs(remaining_points) > 0.01:  # Use a small threshold for floating point comparison
            # Recalculate adjustable keys
            if remaining_points > 0:  # We need to increase other stats more
                adjustable_keys = [k for k in other_keys if self.setup[k] < 10]
            else:  # We need to decrease other stats more
                adjustable_keys = [k for k in other_keys if self.setup[k] > 1]
            
            # Try another round of distribution if we have adjustable keys
            if adjustable_keys:
                points_per_key = remaining_points / len(adjustable_keys)
                for adjust_key in adjustable_keys:
                    # Similar logic as before
                    if points_per_key > 0:
                        max_increase = 10 - self.setup[adjust_key]
                        adjustment = min(points_per_key, max_increase)
                    else:
                        max_decrease = self.setup[adjust_key] - 1
                        adjustment = max(points_per_key, -max_decrease)
                    
                    self.setup[adjust_key] += adjustment
                    remaining_points -= adjustment
                    
                    # Stop if we've distributed all points
                    if abs(remaining_points) < 0.01:
                        break
            
            # If we still couldn't distribute all points, revert the original change
            if abs(remaining_points) > 0.01:
                # Revert all changes
                self.setup[key] = old_value
                for adjust_key in other_keys:
                    self.setup[adjust_key] = round(self.setup[adjust_key])  # Round to avoid floating point issues
                return
        
        # Round all values to integers to avoid floating point issues
        for k in self.setup:
            self.setup[k] = round(self.setup[k])
        
        # Update car performance based on new setup
        self.update_performance_from_setup()