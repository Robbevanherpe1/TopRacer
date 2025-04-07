import pygame
import random
import math
from constants import *

class Animation:
    def __init__(self, screen):
        self.screen = screen
        self.title_y_offset = 0
        self.title_direction = 1
        self.bg_tiles = []
        self.generate_background_tiles()
    
    def generate_background_tiles(self):
        """Generate animated background tiles for the start screen"""
        self.bg_tiles = []
        tile_count = 50  # More tiles for a richer background
        for i in range(tile_count):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(20, 80)
            speed = random.uniform(0.2, 1.5)
            color = random.choice([RED, BLUE, GREEN, YELLOW, PURPLE, CYAN, ORANGE])
            alpha = random.randint(20, 80)  # Transparency value
            self.bg_tiles.append({
                'x': x, 
                'y': y, 
                'size': size, 
                'speed': speed,
                'color': color,
                'alpha': alpha
            })
    
    def draw_background_animation(self):
        """Draw and animate the background tiles on the start screen"""
        # First draw a gradient background
        for y in range(0, SCREEN_HEIGHT, 4):
            # Create gradient from dark blue to black
            color_val = max(0, 50 - int(y * 50 / SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, (0, 0, color_val), (0, y, SCREEN_WIDTH, 4))
            
        # Now draw animated tiles
        for tile in self.bg_tiles:
            # Create a surface with per-pixel alpha for transparency
            s = pygame.Surface((tile['size'], tile['size']), pygame.SRCALPHA)
            # Use the alpha value stored in the tile
            color_with_alpha = (tile['color'][0], tile['color'][1], tile['color'][2], tile['alpha'])
            pygame.draw.rect(s, color_with_alpha, (0, 0, tile['size'], tile['size']))
            self.screen.blit(s, (tile['x'], tile['y']))
    
    def update_start_screen_animation(self):
        """Update the animations on the start screen"""
        # Update title floating animation
        self.title_y_offset += self.title_direction * 0.2
        if self.title_y_offset > 10 or self.title_y_offset < -10:
            self.title_direction *= -1
            
        # Update background tiles movement
        for tile in self.bg_tiles:
            # Move tiles downward
            tile['y'] += tile['speed']
            # If a tile goes off screen, reset it to the top
            if tile['y'] > SCREEN_HEIGHT:
                tile['y'] = -tile['size']
                tile['x'] = random.randint(0, SCREEN_WIDTH)

    def draw_car_preview(self, colors):
        """Draw an animated car preview on the start screen"""
        # Get time for animation
        t = pygame.time.get_ticks() / 1000.0
        
        # Draw multiple cars racing in a circle
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT * 0.75
        radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.2
        
        for i, color in enumerate(colors[:5]):  # Draw 5 cars
            # Calculate position in circle with offset by index
            angle = t * 0.5 + i * (2 * math.pi / 5)
            x = center_x + math.cos(angle) * radius
            y = center_y + math.sin(angle) * radius
            
            # Calculate direction tangent to the circle
            dir_angle = angle + math.pi / 2
            
            # Draw car body (simple rectangle for preview)
            car_width = 14
            car_height = 7
            
            # Create a rotated rectangle
            cos_a = math.cos(dir_angle)
            sin_a = math.sin(dir_angle)
            
            half_width = car_width / 2
            half_height = car_height / 2
            
            # Calculate rotated corners
            corners = []
            for xm, ym in [(-half_width, -half_height), 
                          (half_width, -half_height), 
                          (half_width, half_height), 
                          (-half_width, half_height)]:
                corner_x = x + xm * cos_a - ym * sin_a
                corner_y = y + xm * sin_a + ym * cos_a
                corners.append((corner_x, corner_y))
            
            # Draw the car
            pygame.draw.polygon(self.screen, color, corners)
            pygame.draw.polygon(self.screen, BLACK, corners, 1)