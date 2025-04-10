import pygame
import math
from constants.constants import *
from ui.base_ui import BaseUI

class RaceEndUI(BaseUI):
    """UI component for the race end screen"""
    
    def draw_race_end_screen(self, game, animation):
        """Draw the race end screen showing final positions and rewards"""
        width, height = self.screen.get_size()
        
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
        
        self._draw_results_panel(game, width)
        self._draw_rewards_panel(game, width)
    
    def _draw_results_panel(self, game, width):
        """Draw the results panel showing final positions"""
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
        
        return panel_rect
    
    def _draw_rewards_panel(self, game, width):
        """Draw the rewards panel showing points and XP earned"""
        panel_rect = self._draw_results_panel(game, width)
        height = self.screen.get_size()[1]
        button_y_pos = 0
        
        # Show rewards earned
        if game.last_race_points_earned > 0 or game.last_race_xp_earned > 0:
            # Create rewards panel
            rewards_panel_width = 300
            rewards_panel_height = 120
            rewards_panel_rect = pygame.Rect(
                width//2 - rewards_panel_width//2,
                panel_rect.bottom + 20,
                rewards_panel_width,
                rewards_panel_height
            )
            
            # Draw panel background with pulsing glow effect
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 20 + 10
            s = pygame.Surface((rewards_panel_width, rewards_panel_height), pygame.SRCALPHA)
            s.fill((40, 40, 100 + int(pulse), 220))
            self.screen.blit(s, rewards_panel_rect)
            pygame.draw.rect(self.screen, YELLOW, rewards_panel_rect, 2)
            
            # Draw rewards title
            rewards_title = self.subtitle_font.render("REWARDS EARNED", True, WHITE)
            self.screen.blit(rewards_title, (rewards_panel_rect.centerx - rewards_title.get_width()//2, 
                                           rewards_panel_rect.y + 15))
            
            # Draw points earned with icon
            points_text = f"+{game.last_race_points_earned} Points"
            points_surface = self.font.render(points_text, True, YELLOW)
            self.screen.blit(points_surface, (rewards_panel_rect.centerx - points_surface.get_width()//2 + 10,
                                           rewards_panel_rect.y + 55))
            
            # Draw star icon for points
            points_icon = self.subtitle_font.render("★", True, YELLOW)
            self.screen.blit(points_icon, (rewards_panel_rect.centerx - points_surface.get_width()//2 - 15,
                                         rewards_panel_rect.y + 53))
            
            # Draw XP earned with icon
            xp_text = f"+{game.last_race_xp_earned} Team Rating"
            xp_surface = self.font.render(xp_text, True, CYAN)
            self.screen.blit(xp_surface, (rewards_panel_rect.centerx - xp_surface.get_width()//2 + 10,
                                        rewards_panel_rect.y + 85))
            
            # Draw XP icon
            xp_icon = self.subtitle_font.render("↑", True, CYAN)
            self.screen.blit(xp_icon, (rewards_panel_rect.centerx - xp_surface.get_width()//2 - 15,
                                     rewards_panel_rect.y + 83))
            
            # Adjust button position to be below rewards panel
            button_y_pos = rewards_panel_rect.bottom + 20
        else:
            # No rewards, button goes directly below results panel
            button_y_pos = panel_rect.bottom + 40
        
        self._draw_continue_button(game, width, button_y_pos)
    
    def _draw_continue_button(self, game, width, button_y_pos):
        """Draw the button to continue to the customization screen"""
        # Draw "Return to Customization" button
        game.menu_button_rect = pygame.Rect(width//2 - 150, button_y_pos, 300, 60)
        
        # Button background with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        button_bg_color = (0, 0, int(pulse))
        pygame.draw.rect(self.screen, button_bg_color, game.menu_button_rect)
        pygame.draw.rect(self.screen, CYAN, game.menu_button_rect, 2, border_radius=10)
        
        # Button text - changed to reflect going to customization screen
        button_text = "Customize Cars"
        button_surface = self.subtitle_font.render(button_text, True, WHITE)
        button_text_pos = (game.menu_button_rect.centerx - button_surface.get_width()//2, 
                          game.menu_button_rect.centery - button_surface.get_height()//2)
        self.screen.blit(button_surface, button_text_pos)
        
        # Additional hint text
        hint_text = "Adjust your cars' setup for the next race"
        hint_surface = self.font.render(hint_text, True, (180, 180, 200))
        self.screen.blit(hint_surface, (width//2 - hint_surface.get_width()//2, game.menu_button_rect.bottom + 10))