import pygame
from constants import *
from ui.base_ui import BaseUI

class RaceUI(BaseUI):
    """UI component for the main racing screen"""
    
    def draw_ui(self, game):
        """Draw the main racing UI elements during gameplay"""
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