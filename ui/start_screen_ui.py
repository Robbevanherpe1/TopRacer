import pygame
import math
from constants import *
from ui.base_ui import BaseUI

class StartScreenUI(BaseUI):
    """UI component for the game's start/title screen"""
    
    def draw_start_screen(self, game, animation):
        """Draw the game's title screen with team selection"""
        width, height = self.screen.get_size()
        animation.draw_background_animation()
        
        title = "TopRacer"
        subtitle = "Racing Management Game"
        instructions = "Select your team or create a new one"
        extra_info = "ESC - Exit | SPACE - Continue with selected team"
        version = "v1.1"
        
        title_surface = self.title_font.render(title, True, WHITE)
        subtitle_surface = self.subtitle_font.render(subtitle, True, CYAN)
        instructions_surface = self.subtitle_font.render(instructions, True, WHITE)
        info_surface = self.font.render(extra_info, True, (180, 180, 180))
        version_surface = self.font.render(version, True, (100, 100, 100))
        
        # Draw the title with a shadow effect
        shadow_offset = 2
        title_shadow = self.title_font.render(title, True, (40, 40, 100))
        
        self.screen.blit(title_shadow, (width//2 - title_surface.get_width()//2 + shadow_offset, 
                                      height//4 + animation.title_y_offset + shadow_offset))
        self.screen.blit(title_surface, (width//2 - title_surface.get_width()//2, 
                                      height//4 + animation.title_y_offset))
        
        # Draw subtitle
        self.screen.blit(subtitle_surface, (width//2 - subtitle_surface.get_width()//2, 
                                          height//4 + 80))
        
        # Draw the player selection area
        self._draw_player_selection_panel(game, width, height)
        
        # Draw instructions and additional info
        self.screen.blit(instructions_surface, (width//2 - instructions_surface.get_width()//2, 
                                            height - 120))
        self.screen.blit(info_surface, (width//2 - info_surface.get_width()//2, 
                                    height - 80))
        
        # Draw version in bottom right
        self.screen.blit(version_surface, (width - version_surface.get_width() - 10, 
                                        height - version_surface.get_height() - 10))
        
        # Draw car animation on the start screen
        animation.draw_car_preview(game.colors)
        
    def _draw_player_selection_panel(self, game, width, height):
        """Draw the player selection panel with team options"""
        # Create panel for player selection
        panel_width = 500
        panel_height = 400
        panel_rect = pygame.Rect(width//2 - panel_width//2, height//2 - 50, panel_width, panel_height)
        
        # Semi-transparent panel background
        s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        s.fill((20, 20, 60, 180))
        self.screen.blit(s, panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 220), panel_rect, 2)
        
        # Panel title
        panel_title = self.subtitle_font.render("SELECT TEAM", True, WHITE)
        self.screen.blit(panel_title, (panel_rect.centerx - panel_title.get_width()//2, panel_rect.y + 15))
        
        # Draw player list with selection highlighting
        player_y = panel_rect.y + 60
        player_height = 50
        button_margin = 10
        
        # Clear button lists
        game.player_buttons = []
        game.delete_buttons = []
        
        for i, player_name in enumerate(game.available_player_names):
            # Player selection button
            button_rect = pygame.Rect(panel_rect.x + 20, player_y, panel_width - 100, player_height)
            game.player_buttons.append(button_rect)
            
            # Highlight selected player
            if i == game.selected_player_index:
                pygame.draw.rect(self.screen, (60, 60, 120), button_rect)
                pygame.draw.rect(self.screen, (150, 150, 255), button_rect, 2)
                text_color = WHITE
            else:
                pygame.draw.rect(self.screen, (40, 40, 80), button_rect)
                pygame.draw.rect(self.screen, (80, 80, 180), button_rect, 1)
                text_color = (200, 200, 200)
            
            # Player name
            player_text = self.font.render(player_name, True, text_color)
            self.screen.blit(player_text, (button_rect.x + 15, button_rect.centery - player_text.get_height()//2))
            
            # Player stats
            if player_name in game.players:
                stats = game.players[player_name]
                stats_text = f"Points: {stats['points']} | Rating: {stats['team_rating']} | Wins: {stats['races_won']}"
                stats_surface = pygame.font.Font(None, 20).render(stats_text, True, (180, 180, 220))
                self.screen.blit(stats_surface, (button_rect.x + 15, button_rect.centery + 10))
            
            # Delete button
            delete_rect = pygame.Rect(button_rect.right + button_margin, player_y, 60, player_height)
            game.delete_buttons.append(delete_rect)
            pygame.draw.rect(self.screen, (100, 40, 40), delete_rect)
            pygame.draw.rect(self.screen, (150, 60, 60), delete_rect, 1)
            
            delete_text = self.font.render("Delete", True, (220, 200, 200))
            self.screen.blit(delete_text, (delete_rect.centerx - delete_text.get_width()//2, delete_rect.centery - delete_text.get_height()//2))
            
            player_y += player_height + button_margin
        
        self._draw_add_player_button(game, panel_rect)
        self._draw_input_field(game, panel_rect)
        
    def _draw_add_player_button(self, game, panel_rect):
        """Draw the 'Add New Team' button"""
        game.add_player_button_rect = pygame.Rect(
            panel_rect.centerx - 100, 
            panel_rect.bottom - 60,
            200, 40
        )
        
        # Button with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        button_bg_color = (0, int(pulse * 0.5), 0)
        pygame.draw.rect(self.screen, button_bg_color, game.add_player_button_rect)
        pygame.draw.rect(self.screen, GREEN, game.add_player_button_rect, 2)
        
        add_text = self.font.render("Add New Team", True, WHITE)
        self.screen.blit(add_text, (game.add_player_button_rect.centerx - add_text.get_width()//2, 
                                    game.add_player_button_rect.centery - add_text.get_height()//2))
                                    
    def _draw_input_field(self, game, panel_rect):
        """Draw the input field for adding a new team name"""
        # Show input field when adding a new player
        if game.adding_new_player:
            input_y = panel_rect.bottom - 110
            input_width = 300
            input_height = 40
            
            game.input_rect = pygame.Rect(
                panel_rect.centerx - input_width//2,
                input_y,
                input_width,
                input_height
            )
            
            # Input field background
            pygame.draw.rect(self.screen, (50, 50, 80), game.input_rect)
            pygame.draw.rect(self.screen, (120, 120, 200) if game.input_active else (80, 80, 150), game.input_rect, 2)
            
            # Input text or placeholder
            if game.new_player_name:
                input_text = self.font.render(game.new_player_name, True, WHITE)
            else:
                input_text = self.font.render("Enter team name...", True, (150, 150, 150))
            
            self.screen.blit(input_text, (game.input_rect.x + 10, game.input_rect.centery - input_text.get_height()//2))
            
            # Show instruction
            help_text = self.font.render("Press ENTER to confirm", True, (180, 180, 220))
            self.screen.blit(help_text, (game.input_rect.centerx - help_text.get_width()//2, game.input_rect.bottom + 10))