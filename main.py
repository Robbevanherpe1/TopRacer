import pygame
import sys
from track import Track
from car import Car
import random
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920  # 1080p resolution width
SCREEN_HEIGHT = 1080  # 1080p resolution height
FPS = 60

# Camera constants
CAMERA_SMOOTHNESS = 0.1  # Lower = smoother but slower camera (between 0.01 and 1.0)

# Game states
STATE_START_SCREEN = 0
STATE_RACING = 1
STATE_PAUSE = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Set up the display - add RESIZABLE flag
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("TopRacer - Racing Management Game")
clock = pygame.time.Clock()

# Fonts for UI
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 72)
subtitle_font = pygame.font.SysFont(None, 36)

class Game:
    def __init__(self):
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
            self.cars.append(car)
        
        # Game state
        self.running = True
        self.race_time = 0
        self.message = "Welcome to TopRacer! Press SPACE to start/pause. Arrow keys to select car. P to push."
        self.message_timer = 300

        # Camera position
        self.camera_x = 0
        self.camera_y = 0

        # Game state
        self.state = STATE_START_SCREEN
        
        # Start screen animation values
        self.title_y_offset = 0
        self.title_direction = 1
        self.bg_tiles = []
        self.generate_background_tiles()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Handle window resize events
            if event.type == pygame.VIDEORESIZE:
                global SCREEN_WIDTH, SCREEN_HEIGHT
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == STATE_START_SCREEN:
                        self.state = STATE_RACING
                        self.message = "Race started!"
                        self.message_timer = 180
                    elif self.state == STATE_RACING:
                        self.state = STATE_PAUSE
                        self.message = "Game Paused!"
                        self.message_timer = 180
                    elif self.state == STATE_PAUSE:
                        self.state = STATE_RACING
                        self.message = "Race resumed!"
                        self.message_timer = 180
                        
                # Exit the game with Escape key
                if event.key == pygame.K_ESCAPE and self.state != STATE_START_SCREEN:
                    self.state = STATE_START_SCREEN
                    self.message = "Returned to start screen!"
                    self.message_timer = 180
                
                # Select different engineer car with arrow keys
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
                if event.key == pygame.K_p:
                    selected_car = self.cars[self.selected_car_index]
                    response = selected_car.toggle_push_mode()
                    self.message = response
                    self.message_timer = 180
    
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
        
        if self.state == STATE_START_SCREEN:
            self.update_start_screen_animation()
    
    def draw(self):
        # Fill screen with background color
        screen.fill(BLACK)
        
        if self.state == STATE_START_SCREEN:
            self.draw_start_screen()
        else:
            # Draw the track
            self.track.draw(screen, self.camera_x, self.camera_y)
            
            # Draw all cars
            for i, car in enumerate(self.cars):
                car.draw(screen, self.camera_x, self.camera_y)
                
                # Add indicator for selected car - Fix: ensuring position is integer
                if i == self.selected_car_index:
                    pos_x = int(car.x - self.camera_x)
                    pos_y = int(car.y - self.camera_y)
                    pygame.draw.circle(screen, WHITE, (pos_x, pos_y), 18, 1)  # Reduced from 25 to match smaller car size
            
            # Draw UI
            self.draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def draw_start_screen(self):
        self.draw_background_animation()
        
        title = "TopRacer"
        subtitle = "Racing Management Game"
        instructions = "Press SPACE to start the race"
        extra_info = "ESC - Return to menu | Arrow keys - Select car | P - Push"
        version = "v1.0"
        
        title_surface = title_font.render(title, True, WHITE)
        subtitle_surface = subtitle_font.render(subtitle, True, CYAN)
        instructions_surface = subtitle_font.render(instructions, True, WHITE)
        info_surface = font.render(extra_info, True, (180, 180, 180))
        version_surface = font.render(version, True, (100, 100, 100))
        
        # Draw the title with a shadow effect
        shadow_offset = 2
        title_shadow = title_font.render(title, True, (40, 40, 100))
        screen.blit(title_shadow, (SCREEN_WIDTH//2 - title_surface.get_width()//2 + shadow_offset, 
                                  SCREEN_HEIGHT//2 - 80 + self.title_y_offset + shadow_offset))
        screen.blit(title_surface, (SCREEN_WIDTH//2 - title_surface.get_width()//2, 
                                  SCREEN_HEIGHT//2 - 80 + self.title_y_offset))
        
        # Draw subtitle
        screen.blit(subtitle_surface, (SCREEN_WIDTH//2 - subtitle_surface.get_width()//2, 
                                      SCREEN_HEIGHT//2 - 20))
                                      
        # Draw a pulsing rectangle around the instructions for emphasis
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        rect = instructions_surface.get_rect()
        rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
        rect = rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, int(pulse)), rect, 2, 3)
                                      
        # Draw instructions and additional info
        screen.blit(instructions_surface, (SCREEN_WIDTH//2 - instructions_surface.get_width()//2, 
                                        SCREEN_HEIGHT//2 + 40))
        screen.blit(info_surface, (SCREEN_WIDTH//2 - info_surface.get_width()//2, 
                                SCREEN_HEIGHT//2 + 100))
                                
        # Draw version in bottom right
        screen.blit(version_surface, (SCREEN_WIDTH - version_surface.get_width() - 10, 
                                    SCREEN_HEIGHT - version_surface.get_height() - 10))
        
        # Draw car animation on the start screen
        self.draw_car_preview()
    
    def draw_ui(self):
        # Draw status of all cars, with engineer cars displayed more prominently
        y_offset = 10
        
        # First section title for engineer cars
        header = "YOUR RACING TEAMS:"
        header_surface = font.render(header, True, (255, 255, 100))  # Bright yellow
        screen.blit(header_surface, (10, y_offset))
        y_offset += 25
        
        # Draw engineer cars first
        for i in self.engineer_car_indices:
            car = self.cars[i]
            status_text = car.get_status()
            
            # Highlight selected car
            if i == self.selected_car_index:
                status_text = "> " + status_text + " ★"
                color = WHITE
            else:
                # Add a star symbol to indicate engineer cars
                status_text = "  " + status_text + " ★"
                color = car.color
                
            status_surface = font.render(status_text, True, color)
            screen.blit(status_surface, (10, y_offset))
            y_offset += 25
            
        # Add a separator and title for other cars    
        y_offset += 10
        header = "OTHER COMPETITORS:"
        header_surface = font.render(header, True, (150, 150, 150))  # Gray
        screen.blit(header_surface, (10, y_offset))
        y_offset += 25
        
        # Draw non-engineer cars
        for i, car in enumerate(self.cars):
            if i not in self.engineer_car_indices:
                status_text = car.get_status()
                color = (120, 120, 120)  # Dimmed color for AI cars
                
                status_surface = font.render(status_text, True, color)
                screen.blit(status_surface, (10, y_offset))
                y_offset += 25
        
        # Draw race time
        minutes = self.race_time // (60 * 60)
        seconds = (self.race_time // 60) % 60
        time_text = f"Race Time: {minutes:02d}:{seconds:02d}"
        time_surface = font.render(time_text, True, WHITE)
        screen.blit(time_surface, (SCREEN_WIDTH - time_surface.get_width() - 10, 10))
        
        # Draw current message
        if self.message_timer > 0:
            message_surface = font.render(self.message, True, WHITE)
            screen.blit(message_surface, 
                       (SCREEN_WIDTH//2 - message_surface.get_width()//2, 
                        SCREEN_HEIGHT - 30))
        
        # Draw controls help with emphasis on engineer cars
        controls = "Controls: SPACE - Pause, Arrows - Select Team, P - Push Mode"
        controls_surface = font.render(controls, True, WHITE)
        screen.blit(controls_surface, 
                   (SCREEN_WIDTH//2 - controls_surface.get_width()//2, 
                    SCREEN_HEIGHT - 60))
    
    def run(self):
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            clock.tick(FPS)
    
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
            pygame.draw.rect(screen, (0, 0, color_val), (0, y, SCREEN_WIDTH, 4))
            
        # Now draw animated tiles
        for tile in self.bg_tiles:
            # Create a surface with per-pixel alpha for transparency
            s = pygame.Surface((tile['size'], tile['size']), pygame.SRCALPHA)
            # Use the alpha value stored in the tile
            color_with_alpha = (tile['color'][0], tile['color'][1], tile['color'][2], tile['alpha'])
            pygame.draw.rect(s, color_with_alpha, (0, 0, tile['size'], tile['size']))
            screen.blit(s, (tile['x'], tile['y']))
    
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

    def draw_car_preview(self):
        """Draw an animated car preview on the start screen"""
        # Get time for animation
        t = pygame.time.get_ticks() / 1000.0
        
        # Draw multiple cars racing in a circle
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT * 0.75
        radius = min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.2
        
        for i, color in enumerate(self.colors[:5]):  # Draw 5 cars
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
            pygame.draw.polygon(screen, color, corners)
            pygame.draw.polygon(screen, BLACK, corners, 1)

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()