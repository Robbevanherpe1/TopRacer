import pygame
import sys
from constants import *
from game import Game
from ui import UI
from animation import Animation

def main():
    # Initialize pygame
    pygame.init()
    
    # Initialize fonts directly here instead of using the constants.init_fonts() function
    global font, title_font, subtitle_font
    pygame.font.init()  # Ensure the font module is initialized
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 36)
    
    print("Fonts initialized directly:", font, title_font, subtitle_font)
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("TopRacer - Racing Management Game")
    clock = pygame.time.Clock()
    
    # Initialize game components
    game = Game(screen)
    ui = UI(screen)
    animation = Animation(screen)
    
    # Main game loop
    while game.running:
        # Handle events
        game.handle_events()
        
        # Update game state
        if game.state == STATE_RACING:
            game.update()
        elif game.state == STATE_START_SCREEN:
            animation.update_start_screen_animation()
        
        # Clear screen
        screen.fill(BLACK)
        
        # Draw current game state
        if game.state == STATE_START_SCREEN:
            ui.draw_start_screen(game, animation)
        elif game.state == STATE_CUSTOMIZATION:
            ui.draw_customization_screen(game)
        elif game.state == STATE_RACE_END:
            ui.draw_race_end_screen(game, animation)
        else:
            # Draw the track
            game.track.draw(screen, game.camera_x, game.camera_y)
            
            # Draw waypoints if enabled
            if game.show_waypoints:
                game.track.draw_waypoints(screen, game.camera_x, game.camera_y)
            
            # Draw all cars
            for i, car in enumerate(game.cars):
                car.draw(screen, game.camera_x, game.camera_y)
                
                # Add indicator for selected car
                if i == game.selected_car_index:
                    pos_x = int(car.x - game.camera_x)
                    pos_y = int(car.y - game.camera_y)
                    pygame.draw.circle(screen, WHITE, (pos_x, pos_y), 18, 1)
            
            # Draw UI components
            ui.draw_ui(game)
            ui.draw_position_overlay(game)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()
        sys.exit()