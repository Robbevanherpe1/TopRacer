import pygame
import math
from constants.constants import *
from ui.base_ui import BaseUI

class ManufacturerUI(BaseUI):
    """UI component for the manufacturer selection screen with carousel display"""
    
    def __init__(self, screen):
        super().__init__(screen)
        # Available manufacturers
        self.manufacturers = [
            {"name": "Ferrari", "image": "ferrari.png"},
            {"name": "Bentley", "image": "bentley.png"},
            {"name": "BMW", "image": "bmw.png"},
            {"name": "McLaren", "image": "mclearn.png"},
            {"name": "Mercedes", "image": "mercedes.png"},
            {"name": "Nissan", "image": "nissan.png"},
            {"name": "Porsche", "image": "porsche.png"},
            {"name": "Renault", "image": "renault.png"}
        ]
        # Load manufacturer images
        for manufacturer in self.manufacturers:
            manufacturer["sprite"] = pygame.image.load(f"game/assets/{manufacturer['image']}").convert_alpha()
        
        # Carousel properties
        self.current_index = 0
        self.target_rotation = 0
        self.current_rotation = 0
        self.rotation_speed = 0.1
        self.carousel_radius = 400
    
    def draw_manufacturer_selection(self, game):
        """Draw the manufacturer selection screen with a carousel of car manufacturers"""
        width, height = self.screen.get_size()
        
        # Draw a dark background with gradient
        for y in range(0, height, 4):
            # Create gradient from dark blue to darker blue
            color_val = max(0, 30 - int(y * 20 / height))
            pygame.draw.rect(self.screen, (0, 0, color_val), (0, y, width, 4))
        
        # Draw header bar
        header_height = 80
        header_rect = pygame.Rect(0, 0, width, header_height)
        s = pygame.Surface((width, header_height), pygame.SRCALPHA)
        s.fill((20, 20, 50, 220))
        self.screen.blit(s, header_rect)
        pygame.draw.line(self.screen, (100, 100, 200), (0, header_height), (width, header_height), 2)
        
        # Draw profile section (left side of header)
        # Profile picture
        profile_image = pygame.image.load("game/assets/helmet.png")
        profile_image = pygame.transform.scale(profile_image, (60, 60))
        self.screen.blit(profile_image, (20, 10))
        
        # Username and race wins
        username = game.player_username
        race_wins = game.player_races_won
        username_text = self.subtitle_font.render(username, True, WHITE)
        wins_text = self.font.render(f"Races won: {race_wins}", True, (200, 200, 200))
        self.screen.blit(username_text, (100, 15))
        self.screen.blit(wins_text, (100, 50))
        
        # Draw title
        title = "SELECT MANUFACTURER"
        title_surface = self.title_font.render(title, True, WHITE)
        self.screen.blit(title_surface, (width//2 - title_surface.get_width()//2, 100))
        
        # Current manufacturer name
        current_manufacturer = self.manufacturers[self.current_index]
        manufacturer_text = self.subtitle_font.render(current_manufacturer["name"], True, (255, 215, 0))
        self.screen.blit(manufacturer_text, (width//2 - manufacturer_text.get_width()//2, 180))
        
        # Update rotation animation
        self.current_rotation += (self.target_rotation - self.current_rotation) * self.rotation_speed
        
        # Draw carousel of manufacturers
        center_x, center_y = width // 2, height // 2 + 50
        
        # Draw information panel for selected manufacturer
        panel_width = 500
        panel_height = 200
        panel_x = width // 2 - panel_width // 2
        panel_y = height - panel_height - 100
        
        # Draw panel background
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((20, 20, 50, 180))
        self.screen.blit(s, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (100, 100, 200), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw manufacturer info
        info_text = [
            f"Manufacturer: {current_manufacturer['name']}",
            "Click to select this manufacturer",
            "Use arrow keys to rotate carousel"
        ]
        
        for i, text in enumerate(info_text):
            text_surface = self.font.render(text, True, WHITE)
            self.screen.blit(text_surface, (panel_x + 20, panel_y + 20 + i * 30))
        
        # Draw "Back to Garage" button
        button_width = 300
        button_height = 60
        button_x = width // 2 - button_width // 2
        button_y = height - 80
        game.back_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = game.back_button_rect.collidepoint(mouse_pos)
        
        # Button with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        button_bg_color = (0, int(pulse * 0.7), int(pulse)) if button_hovered else (0, 0, int(pulse))
        
        pygame.draw.rect(self.screen, button_bg_color, game.back_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, CYAN, game.back_button_rect, 2, border_radius=10)
        
        # Button text
        button_text = "BACK TO GARAGE"
        button_surface = self.subtitle_font.render(button_text, True, WHITE)
        button_text_pos = (
            game.back_button_rect.centerx - button_surface.get_width() // 2,
            game.back_button_rect.centery - button_surface.get_height() // 2
        )
        self.screen.blit(button_surface, button_text_pos)
        
        # Draw carousel of manufacturers
        for i, manufacturer in enumerate(self.manufacturers):
            # Calculate position in carousel
            angle = self.current_rotation + (i * (360 / len(self.manufacturers)))
            rads = math.radians(angle)
            
            # Calculate position with perspective effect
            distance_factor = (math.cos(rads) + 1) / 2  # 0 to 1 range
            
            # Calculate size based on distance (perspective effect)
            base_size = 200
            size = int(base_size * (0.4 + 0.6 * distance_factor))  # Smaller when further
            
            # Calculate position
            x = center_x + math.sin(rads) * self.carousel_radius
            y = center_y - 50 * math.cos(rads)  # Slight vertical displacement
            
            # Draw the manufacturer image with perspective
            sprite = manufacturer["sprite"]
            scaled_sprite = pygame.transform.scale(sprite, (size, size))
            
            # Add transparency effect for cars in the back
            if math.cos(rads) < 0:
                # Create a surface with per-surface alpha
                alpha = int(128 + 127 * distance_factor)  # 128-255 range
                scaled_sprite.set_alpha(alpha)
            else:
                scaled_sprite.set_alpha(255)  # Full opacity for front-facing cars
                
            sprite_rect = scaled_sprite.get_rect(center=(x, y))
            self.screen.blit(scaled_sprite, sprite_rect)
            
            # Highlight the selected manufacturer
            if i == self.current_index:
                # Draw selection indicator
                highlight_rect = pygame.Rect(
                    sprite_rect.x - 10, 
                    sprite_rect.y - 10, 
                    sprite_rect.width + 20, 
                    sprite_rect.height + 20
                )
                pygame.draw.rect(self.screen, YELLOW, highlight_rect, 3, border_radius=15)
        
        # Draw left/right navigation arrows
        arrow_y = center_y
        arrow_size = 40
        
        # Left arrow
        left_arrow_points = [
            (width // 4, arrow_y),
            (width // 4 + arrow_size, arrow_y - arrow_size // 2),
            (width // 4 + arrow_size, arrow_y + arrow_size // 2)
        ]
        pygame.draw.polygon(self.screen, (200, 200, 255), left_arrow_points)
        
        # Right arrow
        right_arrow_points = [
            (3 * width // 4, arrow_y),
            (3 * width // 4 - arrow_size, arrow_y - arrow_size // 2),
            (3 * width // 4 - arrow_size, arrow_y + arrow_size // 2)
        ]
        pygame.draw.polygon(self.screen, (200, 200, 255), right_arrow_points)
        
        # Store active regions for arrows for interaction
        game.left_arrow_rect = pygame.Rect(width // 4 - 30, arrow_y - 30, 60, 60)
        game.right_arrow_rect = pygame.Rect(3 * width // 4 - 30, arrow_y - 30, 60, 60)
    
    def rotate_carousel_left(self):
        """Rotate carousel to the left (next manufacturer)"""
        self.current_index = (self.current_index + 1) % len(self.manufacturers)
        self.target_rotation -= 360 / len(self.manufacturers)

    def rotate_carousel_right(self):
        """Rotate carousel to the right (previous manufacturer)"""
        self.current_index = (self.current_index - 1) % len(self.manufacturers)
        self.target_rotation += 360 / len(self.manufacturers)
    
    def get_selected_manufacturer(self):
        """Return the currently selected manufacturer"""
        return self.manufacturers[self.current_index]