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
        
        # Add new player button
        button_y = player_y
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
        
        # Draw instructions and additional info
        self.screen.blit(instructions_surface, (width//2 - instructions_surface.get_width()//2, 
                                            panel_rect.bottom + 30))
        self.screen.blit(info_surface, (width//2 - info_surface.get_width()//2, 
                                    panel_rect.bottom + 70))
        
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
        
        # Removed default rectangle car representation
        # Removed wheel drawing
        if car.sprite:
            # Draw the sprite instead of the rectangle
            scaled_sprite = pygame.transform.scale(car.sprite, (120, 160))
            rect = scaled_sprite.get_rect(center=car_rect.center)
            self.screen.blit(scaled_sprite, rect)
        
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
        
        # Calculate total balance for all engineer cars
        total_balance = sum(car.setup.values())
        balance_color = (200, 200, 255) if total_balance == 25 else (255, 100, 100)
        
        # Check if all engineer cars are balanced
        all_cars_balanced = True
        for car_idx in game.engineer_car_indices:
            if sum(game.cars[car_idx].setup.values()) != 25:
                all_cars_balanced = False
                break
        
        # Draw balance indicator with highlighting if not balanced
        balance_text = f"Setup Balance: {total_balance}/25"
        balance_text_surface = self.font.render(balance_text, True, balance_color)
        self.screen.blit(balance_text_surface, (setup_panel_rect.centerx - balance_text_surface.get_width()//2, setup_panel_rect.y + 50))
        
        # Check if we're in an active race (sliders should be disabled)
        in_active_race = game.state == STATE_RACING or game.state == STATE_PAUSE
        
        y_offset = setup_panel_rect.y + 80
        option_height = 60
        game.setup_sliders = {}  # Reset sliders
        
        for key, value in options:
            # Option name
            name_text = self.font.render(key, True, (200, 200, 255) if not in_active_race else (150, 150, 180))
            self.screen.blit(name_text, (setup_panel_rect.x + 20, y_offset))
            
            # Value bar
            bar_width = 200
            bar_height = 20
            bar_x = setup_panel_rect.x + 20
            bar_y = y_offset + 30
            
            # Store slider info for interaction
            slider_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
            game.setup_sliders[key] = {"rect": slider_rect, "value": value, "max": 10}
            
            # Check for slider interaction - only if not in active race
            slider_hovered = slider_rect.collidepoint(mouse_pos) and not in_active_race
            
            # Handle slider dragging - only if not in active race
            if slider_hovered and mouse_pressed and not in_active_race:
                game.active_slider = key
            
            if game.active_slider == key and mouse_pressed and not in_active_race:
                # Store old value to calculate difference
                old_value = car.setup[key]
                
                # Calculate new value based on mouse x position
                rel_x = max(0, min(mouse_pos[0] - bar_x, bar_width))
                new_value = max(1, min(10, int((rel_x / bar_width) * 10) + 1))
                
                # Only proceed if the value actually changed
                if new_value != old_value:
                    # Apply the balanced setup adjustment
                    car.adjust_setup_balanced(key, new_value)
            elif game.active_slider == key and not mouse_pressed:
                # Release slider when mouse button is released
                game.active_slider = None
                
            # Draw empty bar
            bg_color = (60, 60, 100) if (slider_hovered or game.active_slider == key) and not in_active_race else (50, 50, 80)
            if in_active_race:
                bg_color = (40, 40, 60)  # Darker background when in race
            pygame.draw.rect(self.screen, bg_color, (bar_x, bar_y, bar_width, bar_height))
            
            # Draw filled portion
            fill_width = int(bar_width * (value / 10))
            # Colors for indicating value compared to baseline of 5
            if value > 5:
                if in_active_race:
                    fill_color = (60, 150, 90)  # Darker green when in race
                else:
                    fill_color = (100, 255, 150) if slider_hovered or game.active_slider == key else (80, 200, 120)
            elif value < 5:
                if in_active_race:
                    fill_color = (150, 90, 60)  # Darker red when in race
                else:
                    fill_color = (255, 150, 100) if slider_hovered or game.active_slider == key else (200, 120, 80)
            else:
                if in_active_race:
                    fill_color = (80, 110, 160)  # Darker blue when in race
                else:
                    fill_color = (150, 200, 255) if slider_hovered or game.active_slider == key else (100, 150, 250)
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            # Draw baseline marker at value 5
            baseline_x = bar_x + int(bar_width * (5 / 10))
            pygame.draw.line(self.screen, (220, 220, 220), (baseline_x, bar_y), (baseline_x, bar_y + bar_height), 2)
            
            # Draw border
            border_color = (150, 150, 230) if (slider_hovered or game.active_slider == key) and not in_active_race else (100, 100, 180)
            if in_active_race:
                border_color = (80, 80, 130)  # Darker border when in race
            pygame.draw.rect(self.screen, border_color, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Draw value text
            value_text = self.font.render(f"{value}/10", True, WHITE if not in_active_race else (180, 180, 180))
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
                
            desc_text = pygame.font.Font(None, 20).render(description, True, (170, 170, 200) if not in_active_race else (130, 130, 160))
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
        
        # Draw permanent upgrades section
        upgrade_description = "Permanent upgrades boost performance of both cars:"
        upgrade_desc_text = self.font.render(upgrade_description, True, (220, 220, 255))
        self.screen.blit(upgrade_desc_text, (upgrade_panel_rect.x + 20, upgrade_panel_rect.y + 60))
        
        # Define permanent upgrades to display
        permanent_upgrades = [
            {"name": "Engine", "level": game.engine_upgrade_level, "description": "Improves acceleration and top speed"},
            {"name": "Tires", "level": game.tires_upgrade_level, "description": "Improves cornering grip and handling"},
            {"name": "Aerodynamics", "level": game.aero_upgrade_level, "description": "Improves high-speed cornering and top speed"}
        ]
        
        # Draw each upgrade with level indicator and upgrade button
        y_offset = upgrade_panel_rect.y + 90
        button_width = 120
        button_height = 30
        level_bar_width = 150
        level_bar_height = 15
        
        # Store buttons info for mouse interaction
        game.upgrade_buttons = {}
        
        # Store reference to car for upgrades
        if not hasattr(car, 'game'):
            car.game = game
        
        for i, upgrade in enumerate(permanent_upgrades):
            # Upgrade name and current level
            name_text = self.font.render(f"{upgrade['name']}", True, WHITE)
            self.screen.blit(name_text, (upgrade_panel_rect.x + 20, y_offset))
            
            level_text = self.font.render(f"Level {upgrade['level']}/10", True, (220, 220, 255))
            self.screen.blit(level_text, (upgrade_panel_rect.x + upgrade_panel_width - level_text.get_width() - 20, y_offset))
            
            # Draw level bar background
            bar_x = upgrade_panel_rect.x + 20
            bar_y = y_offset + 30
            pygame.draw.rect(self.screen, (50, 50, 80), (bar_x, bar_y, level_bar_width, level_bar_height))
            
            # Draw filled level bar
            fill_width = int(level_bar_width * (upgrade['level'] / 10))
            upgrade_color = (80, 200, 120)  # Green for upgrades
            pygame.draw.rect(self.screen, upgrade_color, (bar_x, bar_y, fill_width, level_bar_height))
            
            # Draw border
            pygame.draw.rect(self.screen, (100, 100, 180), (bar_x, bar_y, level_bar_width, level_bar_height), 1)
            
            # Draw upgrade description
            desc_text = pygame.font.Font(None, 20).render(upgrade['description'], True, (170, 170, 200))
            self.screen.blit(desc_text, (bar_x, bar_y + 20))
            
            # Calculate cost of next upgrade level
            current_level = upgrade['level']
            if current_level < 10:  # Only show upgrade button if not max level
                cost = game.base_upgrade_cost * (current_level + 1)
                
                # Draw upgrade button
                button_x = upgrade_panel_rect.x + upgrade_panel_width - button_width - 20
                button_y = bar_y + 15
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                
                # Store button info
                game.upgrade_buttons[upgrade['name']] = button_rect
                
                button_hovered = button_rect.collidepoint(mouse_pos) and not in_active_race
                can_afford = game.player_points >= cost
                
                # Button colors based on state
                if not can_afford:
                    # Can't afford - red
                    button_color = (100, 50, 50) if not button_hovered else (150, 70, 70)
                    text_color = (200, 150, 150)
                else:
                    # Can afford - green
                    button_color = (50, 100, 50) if not button_hovered else (70, 150, 70)
                    text_color = (150, 220, 150)
                    
                # Disabled in race
                if in_active_race:
                    button_color = (70, 70, 90)
                    text_color = (150, 150, 180)
                
                # Draw button
                pygame.draw.rect(self.screen, button_color, button_rect)
                pygame.draw.rect(self.screen, (100, 100, 150), button_rect, 1)
                
                # Button text
                cost_text = f"Upgrade: {cost}"
                cost_surface = pygame.font.Font(None, 22).render(cost_text, True, text_color)
                cost_pos = (button_rect.centerx - cost_surface.get_width()//2,
                            button_rect.centery - cost_surface.get_height()//2)
                self.screen.blit(cost_surface, cost_pos)
                
                # Handle button clicks
                if button_hovered and mouse_pressed and can_afford and not in_active_race:
                    # Purchase the upgrade
                    if upgrade['name'] == "Engine":
                        game.engine_upgrade_level += 1
                        game.player_points -= cost
                    elif upgrade['name'] == "Tires":
                        game.tires_upgrade_level += 1
                        game.player_points -= cost
                    elif upgrade['name'] == "Aerodynamics":
                        game.aero_upgrade_level += 1
                        game.player_points -= cost
                    
                    # Update car performance with new upgrades
                    for car_idx in game.engineer_car_indices:
                        car = game.cars[car_idx]
                        if not hasattr(car, 'game'):
                            car.game = game
                        car.update_performance_from_setup()
                    
                    game.message = f"{upgrade['name']} upgraded to level {upgrade['level'] + 1}!"
                    game.message_timer = 180
                
            # Move to next upgrade
            y_offset += 80
        
        # Draw setup balance explanation
        balance_explanation = [
            "Setup Balance System:",
            "• Default value for all attributes is 5",
            "• Increasing one attribute above 5",
            "  will decrease others to maintain balance",
            "• Total points must equal 25 (5×5)",
            "• Both cars must have balanced setups!"
        ]
        
        y_offset += 40
        for line in balance_explanation:
            text = self.font.render(line, True, (180, 180, 255))
            self.screen.blit(text, (upgrade_panel_rect.x + 20, y_offset))
            y_offset += 25
        
        # Draw race status message if we're in a race
        if in_active_race:
            status_text = "Race in progress - Setup changes locked"
            status_surface = self.font.render(status_text, True, (255, 200, 100))
            self.screen.blit(status_surface, (setup_panel_rect.centerx - status_surface.get_width()//2, setup_panel_rect.y + setup_panel_height - 40))
            
            status_text2 = "Press ESC to end race and return to this menu"
            status_surface2 = self.font.render(status_text2, True, (200, 200, 200))
            self.screen.blit(status_surface2, (setup_panel_rect.centerx - status_surface2.get_width()//2, setup_panel_rect.y + setup_panel_height - 20))
        
        # Draw "Start Race" button at the bottom - disable if in active race
        button_width = 300
        button_height = 70
        game.start_race_button_rect = pygame.Rect(
            width//2 - button_width//2,
            height - 120,
            button_width,
            button_height
        )
        
        # Check if mouse is over button
        button_hovered = game.start_race_button_rect.collidepoint(mouse_pos) and not in_active_race
        
        # Button background with pulsing effect - disable if balance is not correct or in active race
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        if all_cars_balanced and not in_active_race:
            # Button is enabled
            button_bg_color = (0, int(pulse * 0.7), int(pulse)) if button_hovered else (0, 0, int(pulse))
            button_border_color = GREEN if not button_hovered else (100, 255, 100)
            button_text_color = WHITE
            game.race_button_enabled = True
        else:
            # Button is disabled
            button_bg_color = (60, 60, 80)
            button_border_color = (150, 50, 50) if not all_cars_balanced else (80, 80, 110)
            button_text_color = (180, 180, 180)
            game.race_button_enabled = False
            
        pygame.draw.rect(self.screen, button_bg_color, game.start_race_button_rect)
        pygame.draw.rect(self.screen, button_border_color, game.start_race_button_rect, 3, border_radius=10)
        
        # Button text
        button_text = "START RACE"
        if in_active_race:
            button_text = "RACE IN PROGRESS"
            
        button_surface = self.subtitle_font.render(button_text, True, button_text_color)
        button_text_pos = (
            game.start_race_button_rect.centerx - button_surface.get_width()//2,
            game.start_race_button_rect.centery - button_surface.get_height()//2
        )
        self.screen.blit(button_surface, button_text_pos)
        
        # Draw instruction text or warning
        if not all_cars_balanced:
            instruction = "⚠️ Both engineer cars must have exactly 25 setup points to start!"
            instruction_color = (255, 100, 100)
        elif in_active_race:
            instruction = "Race in progress - Return to the race with ESC"
            instruction_color = (255, 200, 100)
        else:
            instruction = "Drag sliders to adjust car setup. Different setups perform better in different conditions."
            instruction_color = (180, 180, 255)
            
        instruction_surface = self.font.render(instruction, True, instruction_color)
        self.screen.blit(instruction_surface, (width//2 - instruction_surface.get_width()//2, height - 160))