import pygame
import math
from constants import *

class UI:
    def __init__(self, screen):
        self.screen = screen
        
        # Initialize local font objects that won't be affected by module import issues
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)

    def draw_ui(self, game):
        width, height = self.screen.get_size()
        
        # Draw race time
        minutes = game.race_time // (60 * 60)
        seconds = (game.race_time // 60) % 60
        time_text = f"Race Time: {minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_text, True, WHITE)
        self.screen.blit(time_surface, (width - time_surface.get_width() - 10, 10))
        
        # Show waypoint status
        waypoint_status = "Waypoints: ON" if game.show_waypoints else "Waypoints: OFF"
        waypoint_surface = self.font.render(waypoint_status, True, YELLOW if game.show_waypoints else (120, 120, 120))
        self.screen.blit(waypoint_surface, (width - waypoint_surface.get_width() - 10, 40))
        
        # Draw current message
        if game.message_timer > 0:
            message_surface = self.font.render(game.message, True, WHITE)
            self.screen.blit(message_surface, 
                           (width//2 - message_surface.get_width()//2, 
                            height - 30))
        
        # Draw controls help with emphasis on engineer cars
        controls = "Controls: SPACE - Pause, Arrows - Select Team, P - Push, W - Toggle Waypoints"
        controls_surface = self.font.render(controls, True, WHITE)
        self.screen.blit(controls_surface, 
                       (width//2 - controls_surface.get_width()//2, 
                        height - 60))

    def draw_position_overlay(self, game):
        """Draw a nice overlay on the top left of the screen showing race positions"""
        width, height = self.screen.get_size()
        if not game.race_positions:  # Initialize positions if empty
            game.race_positions = list(range(len(game.cars)))
        
        # Draw a semi-transparent background panel for the position display
        panel_width = 260
        panel_height = len(game.cars) * 60 + 80  # Increased block height
        panel_rect = pygame.Rect(20, 20, panel_width, panel_height)  # Moved to top left
        
        # Create a semi-transparent surface
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((20, 20, 50, 180))  # Dark blue with transparency
        self.screen.blit(s, panel_rect)
        
        # Draw border
        pygame.draw.rect(self.screen, (100, 100, 200), panel_rect, 2)
        
        # Draw the "RACE POSITIONS" title
        title_font = pygame.font.SysFont(None, 30)
        title = title_font.render("RACE POSITIONS", True, (220, 220, 255))
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 10))
        
        # Draw lap counter
        lap_text = f"LAP {min(max([car.laps for car in game.cars]) + 1, game.MAX_LAPS)} / {game.MAX_LAPS}"
        lap_font = pygame.font.SysFont(None, 24)
        lap_surface = lap_font.render(lap_text, True, (180, 180, 255))
        self.screen.blit(lap_surface, (panel_rect.centerx - lap_surface.get_width() // 2, panel_rect.y + 35))
        
        # Draw divider line
        pygame.draw.line(self.screen, (100, 100, 200), 
                        (panel_rect.left + 10, panel_rect.y + 55), 
                        (panel_rect.right - 10, panel_rect.y + 55), 2)
        
        # For each car in race positions, draw its position
        position_font = pygame.font.SysFont(None, 26)
        for i, car_idx in enumerate(game.race_positions):
            car = game.cars[car_idx]
            position = i + 1
            
            # Calculate y position for this entry
            y_pos = panel_rect.y + 65 + i * 60  # Adjusted y position
            
            # Highlight any selected car
            if car_idx == game.selected_car_index:
                row_color = (80, 80, 120, 180)  # Distinct background for selected car
                text_color = (255, 255, 0)      # Brighter text
            elif car_idx in game.engineer_car_indices:
                row_color = (60, 60, 90, 180)  # Brighter background for your teams
                text_color = (255, 255, 255)   # Brighter text
            else:
                row_color = (40, 40, 70, 150)  # Darker background for AI teams
                text_color = (180, 180, 180)   # Darker text
                
            # Draw row background
            row_rect = pygame.Rect(panel_rect.x + 5, y_pos, panel_width - 10, 50)  # Adjusted row height
            s = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            s.fill(row_color)
            self.screen.blit(s, row_rect)
            
            # Draw position number in a circle
            circle_x = panel_rect.x + 25
            circle_y = y_pos + 16
            circle_radius = 13
            pygame.draw.circle(self.screen, car.color, (circle_x, circle_y), circle_radius)
            pygame.draw.circle(self.screen, (30, 30, 30), (circle_x, circle_y), circle_radius, 1)
            
            # Draw position number
            pos_text = position_font.render(str(position), True, (30, 30, 30))
            pos_rect = pos_text.get_rect(center=(circle_x, circle_y))
            self.screen.blit(pos_text, pos_rect)
            
            # Draw car name
            name_text = position_font.render(car.name, True, text_color)
            self.screen.blit(name_text, (circle_x + 20, y_pos + 5))  # Adjusted y position
            
            # Show last lap and best lap
            lap_info = f"Lap {car.laps + 1}"
            if car.last_lap_time > 0:
                lap_info += f" | Last: {car.last_lap_time:.2f}s" 
            if car.best_lap is not None:
                lap_info += f" | Best: {car.best_lap:.2f}s"
            lap_text = pygame.font.SysFont(None, 20).render(lap_info, True, text_color)
            self.screen.blit(lap_text, (circle_x + 20, y_pos + 28))  # Adjusted y position

    def draw_start_screen(self, game, animation):
        width, height = self.screen.get_size()
        animation.draw_background_animation()
        
        title = "TopRacer"
        subtitle = "Racing Management Game"
        instructions = "Press SPACE to start the race"
        extra_info = "ESC - Return to menu | Arrow keys - Select car | P - Push"
        version = "v1.0"
        
        title_surface = self.title_font.render(title, True, WHITE)
        subtitle_surface = self.subtitle_font.render(subtitle, True, CYAN)
        instructions_surface = self.subtitle_font.render(instructions, True, WHITE)
        info_surface = self.font.render(extra_info, True, (180, 180, 180))
        version_surface = self.font.render(version, True, (100, 100, 100))
        
        # Draw the title with a shadow effect
        shadow_offset = 2
        title_shadow = self.title_font.render(title, True, (40, 40, 100))
        self.screen.blit(title_shadow, (width//2 - title_surface.get_width()//2 + shadow_offset, 
                                      height//2 - 80 + animation.title_y_offset + shadow_offset))
        self.screen.blit(title_surface, (width//2 - title_surface.get_width()//2, 
                                      height//2 - 80 + animation.title_y_offset))
        
        # Draw subtitle
        self.screen.blit(subtitle_surface, (width//2 - subtitle_surface.get_width()//2, 
                                          height//2 - 20))
                                          
        # Draw a pulsing rectangle around the instructions for emphasis
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        rect = instructions_surface.get_rect()
        rect.center = (width//2, height//2 + 50)
        rect = rect.inflate(20, 10)
        pygame.draw.rect(self.screen, (0, 0, int(pulse)), rect, 2, 3)
                                          
        # Draw instructions and additional info
        self.screen.blit(instructions_surface, (width//2 - instructions_surface.get_width()//2, 
                                            height//2 + 40))
        self.screen.blit(info_surface, (width//2 - info_surface.get_width()//2, 
                                    height//2 + 100))
                                    
        # Draw version in bottom right
        self.screen.blit(version_surface, (width - version_surface.get_width() - 10, 
                                        height - version_surface.get_height() - 10))
        
        # Draw car animation on the start screen
        animation.draw_car_preview(game.colors)
        
    def draw_race_end_screen(self, game, animation):
        width, height = self.screen.get_size()
        """Draw the race end screen showing final positions and a button to return to main menu"""
        # First draw a nice background
        animation.draw_background_animation()
        
        # Create semi-transparent overlay for better text visibility
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 30, 180))  # Dark blue with alpha
        self.screen.blit(overlay, (0, 0))
        
        # Draw race results title
        title_text = "RACE COMPLETE!"
        title_surface = self.title_font.render(title_text, True, WHITE)
        self.screen.blit(title_surface, (width//2 - title_surface.get_width()//2, 50))
        
        # Draw final standings
        subtitle_text = "FINAL STANDINGS"
        subtitle_surface = self.subtitle_font.render(subtitle_text, True, CYAN)
        self.screen.blit(subtitle_surface, (width//2 - subtitle_surface.get_width()//2, 130))
        
        # Create a results panel in the center
        panel_width = 500
        panel_height = len(game.cars) * 50 + 60
        panel_rect = pygame.Rect(width//2 - panel_width//2, 180, panel_width, panel_height)
        
        # Draw panel background
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((20, 20, 60, 200))
        self.screen.blit(s, panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 220), panel_rect, 2)
        
        # Draw each position in the final results
        position_font = pygame.font.SysFont(None, 36)
        detail_font = pygame.font.SysFont(None, 24)
        
        for i, car_idx in enumerate(game.final_positions):
            car = game.cars[car_idx]
            position = i + 1
            
            # Calculate y position for this entry
            y_pos = panel_rect.y + 30 + i * 50
            
            # Determine trophy for top 3
            trophy = ""
            trophy_color = WHITE
            if position == 1:
                trophy = "🏆 "  # Gold trophy
                trophy_color = YELLOW
            elif position == 2:
                trophy = "🥈 "  # Silver medal
                trophy_color = (200, 200, 200)  # Silver
            elif position == 3:
                trophy = "🥉 "  # Bronze medal
                trophy_color = (205, 127, 50)  # Bronze
                
            # Highlight engineer cars with brighter text
            if car_idx in game.engineer_car_indices:
                name_color = WHITE
                detail_color = (200, 200, 255)
                # Draw a slightly lighter background for engineer cars
                highlight_rect = pygame.Rect(panel_rect.x + 10, y_pos - 5, panel_width - 20, 40)
                pygame.draw.rect(self.screen, (40, 40, 90, 180), highlight_rect)
                pygame.draw.rect(self.screen, (80, 80, 160), highlight_rect, 1)
            else:
                name_color = (180, 180, 180)
                detail_color = (150, 150, 150)
            
            # Draw position number
            pos_text = f"{position}."
            pos_surface = position_font.render(pos_text, True, trophy_color)
            self.screen.blit(pos_surface, (panel_rect.x + 30, y_pos))
            
            # Draw trophy for top 3
            if trophy:
                trophy_surface = pygame.font.SysFont(None, 40).render(trophy, True, trophy_color)
                self.screen.blit(trophy_surface, (panel_rect.x + 60, y_pos - 5))
                name_offset = 100  # More space when trophy is present
            else:
                name_offset = 70
            
            # Draw car name - make engineer cars brighter
            name_text = f"{car.name}"
            name_surface = position_font.render(name_text, True, name_color)
            self.screen.blit(name_surface, (panel_rect.x + name_offset, y_pos))
            
            # Draw best lap time
            if car.best_lap is not None:
                time_text = f"Best Lap: {car.best_lap:.2f}s"
                time_surface = detail_font.render(time_text, True, detail_color)
                self.screen.blit(time_surface, (panel_rect.x + name_offset, y_pos + 30))
        
        # Draw "Return to Main Menu" button
        game.menu_button_rect = pygame.Rect(width//2 - 150, panel_rect.bottom + 40, 300, 60)
        
        # Button background with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        button_bg_color = (0, 0, int(pulse))
        pygame.draw.rect(self.screen, button_bg_color, game.menu_button_rect)
        pygame.draw.rect(self.screen, CYAN, game.menu_button_rect, 2, border_radius=10)
        
        # Button text
        button_text = "Return to Main Menu"
        button_surface = self.subtitle_font.render(button_text, True, WHITE)
        button_text_pos = (game.menu_button_rect.centerx - button_surface.get_width()//2, 
                          game.menu_button_rect.centery - button_surface.get_height()//2)
        self.screen.blit(button_surface, button_text_pos)

    def draw_customization_screen(self, game):
        """Draw the car customization screen where player can set up their car before racing"""
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
        # Mock profile picture
        profile_rect = pygame.Rect(20, 10, 60, 60)
        pygame.draw.rect(self.screen, (100, 100, 180), profile_rect)
        pygame.draw.rect(self.screen, WHITE, profile_rect, 2)
        
        # Username and race wins
        username = game.player_username  # Now using game's player_username
        race_wins = game.player_races_won  # Now using game's player_races_won
        username_text = self.subtitle_font.render(username, True, WHITE)
        wins_text = self.font.render(f"Races won: {race_wins}", True, (200, 200, 200))
        self.screen.blit(username_text, (100, 15))
        self.screen.blit(wins_text, (100, 50))
        
        # Points and team rating (right side of header)
        points = game.player_points  # Now using game's player_points
        team_rating = game.player_team_rating  # Now using game's player_team_rating
        points_text = self.subtitle_font.render(f"Points: {points}", True, YELLOW)
        rating_text = self.font.render(f"Team Rating: {team_rating}", True, (200, 200, 200))
        self.screen.blit(points_text, (width - points_text.get_width() - 20, 15))
        self.screen.blit(rating_text, (width - rating_text.get_width() - 20, 50))
        
        # Draw title
        title = "CAR CUSTOMIZATION"
        title_surface = self.title_font.render(title, True, WHITE)
        self.screen.blit(title_surface, (width//2 - title_surface.get_width()//2, 100))
        
        # Draw car preview section
        preview_width = 600
        preview_height = 400
        preview_rect = pygame.Rect(width//2 - preview_width//2, 180, preview_width, preview_height)
        
        # Draw preview background
        pygame.draw.rect(self.screen, (30, 30, 60), preview_rect)
        pygame.draw.rect(self.screen, (80, 80, 150), preview_rect, 2)
        
        # Draw car preview (simple visualization)
        car = game.cars[game.selected_car_index]
        car_rect_width = 200
        car_rect_height = 100
        car_rect = pygame.Rect(
            preview_rect.centerx - car_rect_width//2,
            preview_rect.centery - car_rect_height//2,
            car_rect_width,
            car_rect_height
        )
        
        # Draw a simplified car representation
        pygame.draw.rect(self.screen, car.color, car_rect)
        pygame.draw.rect(self.screen, (50, 50, 50), car_rect, 2)
        
        # Draw wheels
        wheel_radius = 25
        wheel_color = (40, 40, 40)
        wheel_positions = [
            (car_rect.left + wheel_radius + 10, car_rect.bottom - wheel_radius - 5),
            (car_rect.right - wheel_radius - 10, car_rect.bottom - wheel_radius - 5),
            (car_rect.left + wheel_radius + 10, car_rect.top + wheel_radius + 5),
            (car_rect.right - wheel_radius - 10, car_rect.top + wheel_radius + 5)
        ]
        for pos in wheel_positions:
            pygame.draw.circle(self.screen, wheel_color, pos, wheel_radius)
            pygame.draw.circle(self.screen, (100, 100, 100), pos, wheel_radius - 5)
            
        # Draw car stats in the preview area
        stats_y = preview_rect.y + 30
        stats_font = pygame.font.Font(None, 28)
        
        # Calculate and display derived stats
        max_speed_text = f"Top Speed: {car.max_speed:.1f}"
        accel_text = f"Acceleration: {car.acceleration * 100:.1f}"
        turn_text = f"Cornering: {car.turn_speed:.1f}"
        braking_text = f"Braking: {car.braking:.1f}"
        
        stats_texts = [max_speed_text, accel_text, turn_text, braking_text]
        
        for stat_text in stats_texts:
            text_surface = stats_font.render(stat_text, True, (200, 200, 255))
            self.screen.blit(text_surface, (preview_rect.x + 20, stats_y))
            stats_y += 30
            
        # Draw setup options (left panel)
        setup_panel_width = 350
        setup_panel_height = 500
        setup_panel_rect = pygame.Rect(50, 180, setup_panel_width, setup_panel_height)
        
        # Draw panel background
        s = pygame.Surface((setup_panel_width, setup_panel_height), pygame.SRCALPHA)
        s.fill((20, 20, 50, 180))
        self.screen.blit(s, setup_panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 200), setup_panel_rect, 2)
        
        # Setup options title
        setup_title = self.subtitle_font.render("CAR SETUP", True, WHITE)
        self.screen.blit(setup_title, (setup_panel_rect.centerx - setup_title.get_width()//2, setup_panel_rect.y + 20))
        
        # Get mouse position and state for interaction
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        # Setup options using data from the car
        options = list(car.setup.items())
        
        y_offset = setup_panel_rect.y + 80
        option_height = 60
        game.setup_sliders = {}  # Reset sliders
        
        for key, value in options:
            # Option name
            name_text = self.font.render(key, True, (200, 200, 255))
            self.screen.blit(name_text, (setup_panel_rect.x + 20, y_offset))
            
            # Value bar
            bar_width = 200
            bar_height = 20
            bar_x = setup_panel_rect.x + 20
            bar_y = y_offset + 30
            
            # Store slider info for interaction
            slider_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            game.setup_sliders[key] = {"rect": slider_rect, "value": value, "max": 10}
            
            # Check for slider interaction
            slider_hovered = slider_rect.collidepoint(mouse_pos)
            
            # Handle slider dragging
            if slider_hovered and mouse_pressed:
                game.active_slider = key
            
            if game.active_slider == key and mouse_pressed:
                # Calculate new value based on mouse x position
                rel_x = max(0, min(mouse_pos[0] - bar_x, bar_width))
                new_value = max(1, min(10, int((rel_x / bar_width) * 10) + 1))
                
                # Update the car's setup value
                car.setup[key] = new_value
                car.update_performance_from_setup()
            elif game.active_slider == key and not mouse_pressed:
                # Release slider when mouse button is released
                game.active_slider = None
                
            # Draw empty bar
            bg_color = (60, 60, 100) if slider_hovered or game.active_slider == key else (50, 50, 80)
            pygame.draw.rect(self.screen, bg_color, (bar_x, bar_y, bar_width, bar_height))
            
            # Draw filled portion
            fill_width = int(bar_width * (value / 10))
            fill_color = (150, 200, 255) if slider_hovered or game.active_slider == key else (100, 150, 250)
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            # Draw border
            border_color = (150, 150, 230) if slider_hovered or game.active_slider == key else (100, 100, 180)
            pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Draw value text
            value_text = self.font.render(f"{value}/10", True, WHITE)
            self.screen.blit(value_text, (bar_x + bar_width + 20, bar_y))
            
            # Draw property description
            description = ""
            if key == "Engine":
                description = "Affects top speed and acceleration"
            elif key == "Tires":
                description = "Affects cornering grip and handling"
            elif key == "Aerodynamics":
                description = "Affects top speed and high-speed cornering"
            elif key == "Handling":
                description = "Affects responsiveness in corners"
            elif key == "Brakes":
                description = "Affects braking efficiency"
                
            desc_text = pygame.font.Font(None, 20).render(description, True, (170, 170, 200))
            self.screen.blit(desc_text, (bar_x, bar_y + 25))
            
            y_offset += option_height
        
        # Draw upgrades section (right panel)
        upgrade_panel_width = 350
        upgrade_panel_height = 500
        upgrade_panel_rect = pygame.Rect(width - 50 - upgrade_panel_width, 180, upgrade_panel_width, upgrade_panel_height)
        
        # Draw panel background
        s = pygame.Surface((upgrade_panel_width, upgrade_panel_height), pygame.SRCALPHA)
        s.fill((20, 20, 50, 180))
        self.screen.blit(s, upgrade_panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 200), upgrade_panel_rect, 2)
        
        # Upgrades title
        upgrade_title = self.subtitle_font.render("UPGRADES", True, WHITE)
        self.screen.blit(upgrade_title, (upgrade_panel_rect.centerx - upgrade_title.get_width()//2, upgrade_panel_rect.y + 20))
        
        # Placeholder for future upgrades
        upgrade_message = ["Coming Soon!", "Spend points to upgrade your car", "and improve its performance."]
        y_offset = upgrade_panel_rect.y + 80
        
        for line in upgrade_message:
            text = self.font.render(line, True, (180, 180, 180))
            self.screen.blit(text, (upgrade_panel_rect.centerx - text.get_width()//2, y_offset))
            y_offset += 30
        
        # Draw "Start Race" button at the bottom
        button_width = 300
        button_height = 70
        game.start_race_button_rect = pygame.Rect(
            width//2 - button_width//2,
            height - 120,
            button_width,
            button_height
        )
        
        # Check if mouse is over button
        button_hovered = game.start_race_button_rect.collidepoint(mouse_pos)
        
        # Button background with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        button_bg_color = (0, int(pulse * 0.7), int(pulse)) if button_hovered else (0, 0, int(pulse))
        pygame.draw.rect(self.screen, button_bg_color, game.start_race_button_rect)
        button_border_color = GREEN if not button_hovered else (100, 255, 100)
        pygame.draw.rect(self.screen, button_border_color, game.start_race_button_rect, 3, border_radius=10)
        
        # Button text
        button_text = "START RACE"
        button_surface = self.subtitle_font.render(button_text, True, WHITE)
        button_text_pos = (
            game.start_race_button_rect.centerx - button_surface.get_width()//2,
            game.start_race_button_rect.centery - button_surface.get_height()//2
        )
        self.screen.blit(button_surface, button_text_pos)
        
        # Draw instruction text
        instruction = "Drag sliders to adjust car setup. Different setups perform better in different conditions."
        instruction_surface = self.font.render(instruction, True, (180, 180, 255))
        self.screen.blit(instruction_surface, (width//2 - instruction_surface.get_width()//2, height - 160))