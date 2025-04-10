import pygame
import sys
import math
from constants.constants import *
from gameplay import Game
from ui import UI  # This now uses our controller UI class
from animation.animation import Animation

# Global UI instance that will be accessible to other modules
global_ui = None

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
    
    # Initialize global UI
    global global_ui
    global_ui = UI(screen)
    
    animation = Animation(screen)
    
    # Make UI instance available to game
    game.ui = global_ui
    
    # Initialize car_upgrades if not already set - store upgrades per car and garage
    if not hasattr(game, 'car_upgrades') or game.car_upgrades is None:
        game.car_upgrades = {}
        for car_idx in game.engineer_car_indices:
            car = game.cars[car_idx]
            # Initialize with empty upgrades - will be loaded from saved data later
            game.car_upgrades[car.name] = {"engine": 0, "tires": 0, "aero": 0}
    
    # Enable debug visualization for the track
    game.track.debug_collisions = []
    
    # Configure car parameters to be more forgiving
    for car in game.cars:
        car.game = game
        # Make waypoint detection more forgiving
        car.waypoint_detection_multiplier = 1.5  # Larger radius to detect waypoints
        car.stuck_threshold = 40  # More sensitive stuck detection (was 60)
        # Enable debug logging for this car
        car.debug_mode = True
        # Add recovery grace period
        car.recovery_grace_period = 0
        # Make the car smaller for collision detection
        car.width = 12  # Reduced from 14
        car.height = 6  # Reduced from 7
        
        # Update car performance to reflect loaded upgrade levels
        if car.is_engineer_car and hasattr(game, 'engine_upgrade_level'):
            car.update_performance_from_setup()
    
    # Reset race positions and make cars start at the beginning
    game.reset_race()
    
    # Ensure cars start at spawn points with enough space between them
    spacing = 30  # Increased from 20 to give more room
    for i, car in enumerate(game.cars):
        # Get the start position from the track
        start_x, start_y = game.track.get_start_position()
        
        # Set cars to start at the spawn position
        car.x, car.y = start_x, start_y
        
        # Add offset based on car index to avoid collision at start
        offset_angle = (i * 45) % 360  # Spread cars in different directions
        offset_distance = spacing * ((i // 4) + 1)  # Increase distance for more cars
        
        # Calculate offset position
        radians = math.radians(offset_angle)
        car.x += math.cos(radians) * offset_distance
        car.y += math.sin(radians) * offset_distance
        
        # Set current waypoint to 0 and face toward it
        car.current_waypoint = 0
        car.initialize_car_direction()
        
        # Make sure cars start with zero speed and no avoidance behavior
        car.speed = 0
        if hasattr(car, 'avoidance_counter'):
            car.avoidance_counter = 0
    
    # Add keybinding for toggling collision debug visualization
    collision_debug = False
    
    try:
        # Main game loop
        while game.running:
            # Collect all events once
            events = pygame.event.get()
            
            # Process events locally first for direct controls
            for event in events:
                if event.type == pygame.QUIT:
                    game.running = False
                elif event.type == pygame.KEYDOWN:
                    # Modify debugging keybindings
                    if event.key == pygame.K_c:  # 'C' key toggles collision debug
                        collision_debug = not collision_debug
                        game.track.debug_collisions = [] if collision_debug else None
                    
                    # Handle other keys that need to be processed immediately
                    if event.key == pygame.K_ESCAPE:
                        game.running = False
            
            # Send events to the game for handling game-specific logic
            game.process_events(events)
            
            # Update game state based on current game state
            if game.state == STATE_RACING:
                game.update()
            elif game.state == STATE_START_SCREEN:
                animation.update_start_screen_animation()
            
            # Clear screen
            screen.fill(BLACK)
            
            # Draw current game state
            if game.state == STATE_START_SCREEN:
                global_ui.draw_start_screen(game, animation)
            elif game.state == STATE_CUSTOMIZATION:
                global_ui.draw_customization_screen(game)
            elif game.state == STATE_RACE_END:
                global_ui.draw_race_end_screen(game, animation)
            elif game.state == STATE_MANUFACTURER_SELECTION:
                global_ui.draw_manufacturer_selection(game)
            else:
                # Draw the track
                game.track.draw(screen, game.camera_x, game.camera_y)
                
                # Draw waypoints if enabled
                if game.show_waypoints:
                    game.track.draw_waypoints(screen, game.camera_x, game.camera_y)
                
                # Draw all cars
                for i, car in enumerate(game.cars):
                    car.draw(screen, game.camera_x, game.camera_y)
                
                # Draw UI components
                global_ui.draw_ui(game)
                global_ui.draw_position_overlay(game)
            
            # Update the display
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(FPS)
        
        # Save player data when exiting normally
        game.save_current_player_stats()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always try to save data even on crash
        try:
            game.save_current_player_stats()
        except:
            pass
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()