import math
import random

import pygame


class PositionCar:

    def __init__(self):
        self.stuck_detection_timer = 0
        self.last_position = (self.x, self.y)
        self.stuck_counter = 0
        self.stuck_threshold = 60  # 1 second at 60fps
        self.is_stuck = False
        self.waypoint_cooldown = 0  

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
    
    def update(self, dt):
            """Update car position and handle AI driving"""
            # Initialize recovery grace period if not present
            if not hasattr(self, 'recovery_grace_period'):
                self.recovery_grace_period = 0
                
            if self.crashed:
                self.recovery_timer -= 1
                if self.recovery_timer <= 0:
                    self.crashed = False
                    # Move slightly backward to recover
                    radians = math.radians(self.angle)
                    self.x -= math.cos(radians) * 8  # Increased from 5 for better recovery
                    self.y -= math.sin(radians) * 8
                    
                return
            
            # Check if we should enable pit road on lap 3
            if self.laps == self.pit_road_lap - 1 and self.current_waypoint >= 29:
                # Enable pit road when approaching the pit entrance on lap 3
                self.take_pit_road = True
                self.track.use_pit_road = True
                if not self.pit_road_debug_printed:
                    print(f"{self.name} is taking the pit road on lap {self.laps + 1}")
                    self.pit_road_debug_printed = True
            elif self.laps >= self.pit_road_lap and self.current_waypoint > 5:
                # Disable pit road after exiting it on lap 3
                self.take_pit_road = False
                self.track.use_pit_road = False
            
            # Update push mode counter
            if self.push_mode:
                self.push_remaining -= 1
                if self.push_remaining <= 0:
                    self.push_mode = False
            
            # Decrease waypoint cooldown if it's active
            if self.waypoint_cooldown > 0:
                self.waypoint_cooldown -= 1
            
            # Check if car is stuck
            self.stuck_detection_timer += 1
            if self.stuck_detection_timer >= 30:  # Check every half second
                self.stuck_detection_timer = 0
                current_pos = (self.x, self.y)
                # Calculate distance moved since last check
                distance_moved = math.sqrt((current_pos[0] - self.last_position[0])**2 + 
                                        (current_pos[1] - self.last_position[1])**2)
                
                if distance_moved < 3.0 and self.speed > 0.5:  # If barely moving but trying to move
                    self.stuck_counter += 1
                    if self.debug_mode:
                        pass
                    if self.stuck_counter >= 3:  # Stuck for 3 consecutive checks
                        self.is_stuck = True
                else:
                    self.stuck_counter = 0
                    self.is_stuck = False
                    
                self.last_position = current_pos
                
            # Handle stuck state
            if self.is_stuck:
                # Try to get unstuck by making more aggressive random adjustments
                self.x += random.randint(-15, 15)  # Increased from -10, 10
                self.y += random.randint(-15, 15)
                self.stuck_counter = 0
                self.is_stuck = False
            
            # AI driving logic - Get current target waypoint coordinates using pit road if active
            target_waypoint_pos = self.track.get_waypoint_position(self.current_waypoint, self.take_pit_road)
            waypoint_x, waypoint_y = target_waypoint_pos
            
            # Calculate angle to target waypoint
            dx = waypoint_x - self.x
            dy = waypoint_y - self.y
            target_angle = math.degrees(math.atan2(dy, dx))
            
            # Improved obstacle detection and avoidance
            current_time = pygame.time.get_ticks()
            if current_time - self.last_obstacle_check > self.obstacle_check_interval:
                self.last_obstacle_check = current_time
                # Check for obstacles ahead in driving direction
                look_ahead_distance = 20 + self.speed * 5  # Look further when moving faster
                radians = math.radians(self.angle)
                look_x = self.x + math.cos(radians) * look_ahead_distance
                look_y = self.y + math.sin(radians) * look_ahead_distance
                
                # Check if there's a wall ahead
                if self.track.is_wall(look_x, look_y):
                    # Start avoiding the obstacle with a random direction bias
                    # This helps cars find a way around obstacles
                    if self.avoidance_counter == 0:
                        self.avoidance_angle = random.choice([-1, 1]) * random.randint(30, 90)
                    self.avoidance_counter = 20  # Avoid for 20 frames
                
                # Also check for obstacles to the sides
                side_angle = 45
                side_distance = 15
                
                # Check left side
                left_x = self.x + math.cos(math.radians(self.angle + side_angle)) * side_distance
                left_y = self.y + math.sin(math.radians(self.angle + side_angle)) * side_distance
                left_clear = not self.track.is_wall(left_x, left_y)
                
                # Check right side
                right_x = self.x + math.cos(math.radians(self.angle - side_angle)) * side_distance
                right_y = self.y + math.sin(math.radians(self.angle - side_angle)) * side_distance
                right_clear = not self.track.is_wall(right_x, right_y)
                
                # If one side is clear and the other isn't, steer toward the clear side
                if left_clear and not right_clear and self.avoidance_counter == 0:
                    self.avoidance_angle = 30
                    self.avoidance_counter = 10
                elif right_clear and not left_clear and self.avoidance_counter == 0:
                    self.avoidance_angle = -30
                    self.avoidance_counter = 10
            
            # Apply the avoidance angle if active
            if self.avoidance_counter > 0:
                target_angle = (self.angle + self.avoidance_angle) % 360
                self.avoidance_counter -= 1
            
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
            waypoint_threshold = 45 * self.waypoint_detection_multiplier * (1.1 - (handling_effect - 0.8) * 0.5)  # Threshold varies with handling
            if self.is_engineer_car:
                waypoint_threshold *= 0.9  # Engineer cars follow more precise line
            
            # Only transition to next waypoint if cooldown is zero
            if distance_to_waypoint < waypoint_threshold and self.waypoint_cooldown == 0:
                # Set a cooldown before allowing next waypoint transition
                self.waypoint_cooldown = 10  # Adjust this value as needed
                
                # Get previous waypoint for reference
                prev_waypoint = self.current_waypoint
                
                # Move to next waypoint
                self.current_waypoint = (self.current_waypoint + 1) % len(self.track.waypoints)
                
                # Check if we've completed a lap when returning to waypoint 0
                if self.current_waypoint == 0 and prev_waypoint != 0:
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
            next_wp_pos = self.track.get_waypoint_position(next_wp_idx, self.take_pit_road)
            next_wp_x, next_wp_y = next_wp_pos
            
            # Also look at waypoint after next for better planning
            next2_wp_idx = (self.current_waypoint + 2) % len(self.track.waypoints)
            next2_wp_pos = self.track.get_waypoint_position(next2_wp_idx, self.take_pit_road)
            next2_wp_x, next2_wp_y = next2_wp_pos
            
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
            
            # Smoother speed adjustment in obstacles
            if self.avoidance_counter > 0:
                target_speed *= 0.7  # Slow down while avoiding obstacles
                
            # Convert angle to radians and update position
            radians = math.radians(self.angle)
            self.x += math.cos(radians) * self.speed
            self.y += math.sin(radians) * self.speed
            
            # Check for collision with walls
            self.check_collision()
