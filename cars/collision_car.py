import math


class CollisionCar():

    def __init__(self):
        self.crashed = False
        self.recovery_timer = 0

    def check_collision(self):
        """Check for collisions with walls and handle recovery"""
        # Skip collision detection if recently recovered (add a grace period)
        if hasattr(self, 'recovery_grace_period') and self.recovery_grace_period > 0:
            self.recovery_grace_period -= 1
            return False
            
        # Get the corners of the car
        corners = self.get_corners()
        
        # Forward prediction distance - make it very short
        radians = math.radians(self.angle)
        forward_x = self.x + math.cos(radians) * (self.width * 0.3)  # Reduced from 0.7 to 0.3
        forward_y = self.y + math.sin(radians) * (self.width * 0.3)  # Reduced from 0.7 to 0.3
        
        # Get tile type at forward position for debugging
        tile_at_forward = self.track.get_tile_type_at(forward_x, forward_y)
        
        # Only crash if hitting a real wall (tile type 0)
        if self.track.is_actual_wall(forward_x, forward_y):
            self.crashed = True
            self.recovery_timer = 20  # Shorter recovery time
            self.speed *= 0.5  # Less penalty
            self.avoidance_counter = 0
            # Add grace period to prevent immediate re-collision
            self.recovery_grace_period = 10
            
            return True
        
        # Use a much smaller collision box when checking for obstacles
        center_x, center_y = self.x, self.y
        collision_detected = False
        collision_point = None
        
        # Check for collision at a minimum of corners to reduce false positives
        for i, corner in enumerate(corners):
            cx, cy = corner
            
            # Move each corner 50% closer to the center (extremely reduced)
            new_cx = cx * 0.5 + center_x * 0.5
            new_cy = cy * 0.5 + center_y * 0.5
            
            # Get tile type for debugging
            tile_type = self.track.get_tile_type_at(new_cx, new_cy)
            
            # Only crash on ACTUAL walls (tile type 0), not track boundaries or empty
            if self.track.is_strict_wall(int(new_cx), int(new_cy)):
                collision_detected = True
                collision_point = (new_cx, new_cy, tile_type)
                break
        
        if collision_detected and collision_point:
            self.crashed = True
            self.recovery_timer = 20  # Faster recovery
            self.speed *= 0.5  # Less penalty
            self.avoidance_counter = 0
            # Add grace period to prevent immediate re-collision
            self.recovery_grace_period = 10
            
            return True
            
        return False
    
    def get_corners(self):
        """Get the four corners of the car for collision detection"""
        cos_a = math.cos(math.radians(self.angle))
        sin_a = math.sin(math.radians(self.angle))
        
        # MAJOR BUG FIX: Using much smaller collision box and fixing y coordinate calculation
        half_width = self.width / 2 * 0.7  # Reduced by 30%
        half_height = self.height / 2 * 0.7  # Reduced by 30%
        
        # Calculate rotated corners
        corners = []
        for xm, ym in [(-half_width, -half_height), 
                       (half_width, -half_height), 
                       (half_width, half_height), 
                       (-half_width, half_height)]:
            # CRITICAL BUG FIX: y calculation used self.x instead of self.y
            x = self.x + xm * cos_a - ym * sin_a
            y = self.y + xm * sin_a + ym * cos_a  # This was using self.x incorrectly
            corners.append((x, y))
            
        return corners