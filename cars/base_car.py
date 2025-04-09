import math
import pygame


class BaseCar:

    def __init__(self):
        return
        
        # Initialize other properties as needed...

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
            scaled_sprite = pygame.transform.scale(self.sprite, (40, 55))
            rotated_sprite = pygame.transform.rotate(scaled_sprite, -self.angle + 90)
            rect = rotated_sprite.get_rect(center=(screen_x, screen_y))
            surface.blit(rotated_sprite, rect)

        # Keep star indicator for engineer cars if desired
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
    
    def update_manufacturer(self, manufacturer):
        """Update the car's manufacturer and sprite"""
        self.manufacturer = manufacturer
        try:
            # Map manufacturer names to filenames
            sprite_map = {
                "Ferrari": "ferrari.png",
                "Bentley": "bentley.png",
                "BMW": "bmw.png",
                "McLaren": "mclearn.png",
                "Mercedes": "mercedes.png",
                "Nissan": "nissan.png",
                "Porsche": "porsche.png",
                "Renault": "renault.png"
            }
            filename = sprite_map.get(manufacturer, "ferrari.png")
            self.sprite = pygame.image.load(f"assets/{filename}").convert_alpha()
        except Exception as e:
            print(f"Error loading car sprite for {manufacturer}: {e}")
            # Fallback to default
            self.sprite = pygame.image.load("assets/ferrari.png").convert_alpha()