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
        # Draw status of all cars, with engineer cars displayed more prominently
        y_offset = 10
        x_offset = width - 330  # Start from the right side of the screen
        
        # First section title for engineer cars
        header = "YOUR RACING TEAMS:"
        header_surface = self.font.render(header, True, (255, 255, 100))  # Bright yellow
        self.screen.blit(header_surface, (x_offset, y_offset))
        y_offset += 25
        
        # Draw engineer cars first
        for i in game.engineer_car_indices:
            car = game.cars[i]
            status_text = car.get_status()
            
            # Highlight selected car
            if i == game.selected_car_index:
                status_text = "> " + status_text + " ★"
                color = WHITE
            else:
                # Add a star symbol to indicate engineer cars
                status_text = "  " + status_text + " ★"
                color = car.color
                
            status_surface = self.font.render(status_text, True, color)
            self.screen.blit(status_surface, (x_offset, y_offset))
            y_offset += 25
            
        # Add a separator and title for other cars    
        y_offset += 10
        header = "OTHER COMPETITORS:"
        header_surface = self.font.render(header, True, (150, 150, 150))  # Gray
        self.screen.blit(header_surface, (x_offset, y_offset))
        y_offset += 25
        
        # Draw non-engineer cars
        for i, car in enumerate(game.cars):
            if i not in game.engineer_car_indices:
                status_text = car.get_status()
                color = (120, 120, 120)  # Dimmed color for AI cars
                
                status_surface = self.font.render(status_text, True, color)
                self.screen.blit(status_surface, (x_offset, y_offset))
                y_offset += 25
        
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
        panel_width = 220
        panel_height = len(game.cars) * 40 + 60  # Extra space for title
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
            y_pos = panel_rect.y + 65 + i * 40
            
            # Determine row color - engineer cars (your teams) get brighter rows
            if car_idx in game.engineer_car_indices:
                row_color = (60, 60, 90, 180)  # Brighter background for your teams
                text_color = (255, 255, 255)   # Brighter text
            else:
                row_color = (40, 40, 70, 150)  # Darker background for AI teams
                text_color = (180, 180, 180)   # Darker text
                
            # Draw row background
            row_rect = pygame.Rect(panel_rect.x + 5, y_pos, panel_width - 10, 32)
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
            self.screen.blit(name_text, (circle_x + 20, y_pos + 8))
            
            # Draw lap info
            lap_info = f"Lap {car.laps + 1}"
            if car.best_lap is not None:
                lap_info += f" | {car.best_lap:.2f}s"
            lap_text = pygame.font.SysFont(None, 20).render(lap_info, True, text_color)
            self.screen.blit(lap_text, (circle_x + 20, y_pos + 25 - lap_text.get_height() // 2))

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