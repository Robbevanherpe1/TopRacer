import pygame
import sys
from track import Track
from car import Car
import random

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

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

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TopRacer - Racing Management Game")
clock = pygame.time.Clock()

# Font for UI
font = pygame.font.SysFont(None, 24)

class Game:
    def __init__(self):
        self.track = Track()
        
        # Create cars with different colors
        self.colors = [BLUE, RED, GREEN, YELLOW, PURPLE, CYAN, ORANGE]
        self.cars = []
        self.selected_car_index = 0
        
        # Set up initial cars (3 cars for now)
        for i in range(3):
            color = self.colors[i % len(self.colors)]
            name = f"Car {i+1}"
            car = Car(self.track, color=color, name=name)
            
            # Only the first two cars can use push mode
            if i >= 2:  # Third car and beyond can't use push
                car.can_push = False
                
            self.cars.append(car)
        
        # Game state
        self.running = True
        self.paused = False
        self.race_time = 0
        self.message = "Welcome to TopRacer! Press SPACE to start/pause. Arrow keys to select car. P to push."
        self.message_timer = 300
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.paused:
                        self.message = "Game Paused!"
                    else:
                        self.message = "Race resumed!"
                    self.message_timer = 180
                
                # Select different car with arrow keys
                if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    self.selected_car_index = (self.selected_car_index - 1) % len(self.cars)
                    self.message = f"Selected {self.cars[self.selected_car_index].name}"
                    self.message_timer = 120
                    
                if event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    self.selected_car_index = (self.selected_car_index + 1) % len(self.cars)
                    self.message = f"Selected {self.cars[self.selected_car_index].name}"
                    self.message_timer = 120
                    
                # Engineer commands
                if event.key == pygame.K_p:
                    selected_car = self.cars[self.selected_car_index]
                    response = selected_car.toggle_push_mode()
                    self.message = response
                    self.message_timer = 180
    
    def update(self):
        if not self.paused:
            # Update race time
            self.race_time += 1
            
            # Update all cars
            for car in self.cars:
                car.update(1)
                
            # Update message timer
            if self.message_timer > 0:
                self.message_timer -= 1
    
    def draw(self):
        # Fill screen with background color
        screen.fill(BLACK)
        
        # Draw the track
        self.track.draw(screen)
        
        # Draw all cars
        for i, car in enumerate(self.cars):
            car.draw(screen)
            
            # Add indicator for selected car - Fix: ensuring position is integer
            if i == self.selected_car_index:
                pos_x = int(car.x)
                pos_y = int(car.y)
                pygame.draw.circle(screen, WHITE, (pos_x, pos_y), 25, 1)
        
        # Draw UI
        self.draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def draw_ui(self):
        # Draw status of all cars
        y_offset = 10
        for i, car in enumerate(self.cars):
            status_text = car.get_status()
            
            # Highlight selected car
            if i == self.selected_car_index:
                status_text = "> " + status_text
                color = WHITE
            else:
                color = car.color
                
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
        
        # Draw controls help
        controls = "Controls: SPACE - Pause, Arrows - Select Car, P - Push"
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

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()