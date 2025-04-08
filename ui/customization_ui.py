import pygame
import math
from constants import *
from ui.base_ui import BaseUI

class CustomizationUI(BaseUI):
    """UI component for the car customization screen"""
    
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
        # Profile picture

        profile_image = pygame.image.load("assets/helmet.png")
        profile_image = pygame.transform.scale(profile_image, (60, 60))
        self.screen.blit(profile_image, (20, 10))
        
        # Username and race wins
        username = game.player_username  # Now using game's player_username
        race_wins = game.player_races_won  # Now using game's player_races_won
        username_text = self.subtitle_font.render(username, True, WHITE)
        wins_text = self.font.render(f"Races won: {race_wins}", True, (200, 200, 200))
        self.screen.blit(username_text, (100, 15))
        self.screen.blit(wins_text, (100, 50))



        #Team manufacturer
        #team_manufacturer = game.player_team_manufacturer 
        #team_manufacturer_text = self.font.render(f"Team: {team_manufacturer}", True, (200, 200, 200))

        team_manufacturer_text = self.font.render(f"Manufacturer: ferrari", True, (200, 200, 200))
        self.screen.blit(team_manufacturer_text, (width//2 - team_manufacturer_text.get_width() + 50, 15))

        #current garage
        if game.selected_car_index == 0:
            current_garage = 1
        else:
            current_garage = 2

        current_garage_text = self.font.render(f"Garage: {current_garage}", True, (200, 200, 200))
        self.screen.blit(current_garage_text, (width//2 - current_garage_text.get_width(), 50))
        
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
        car_rect_width = 300
        car_rect_height = 300
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
            scaled_sprite = pygame.transform.scale(car.sprite, (car_rect_width, car_rect_height))
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
            
            y_offset += option_height + 20
        
        # Draw upgrades section (right panel)
        self._draw_upgrades_panel(game, width, height)
        
        # Draw "Start Race" button at the bottom - disable if in active race
        self._draw_race_button(game, width, height, all_cars_balanced, in_active_race)

        # Draw manufacturer selector button
        self._draw_manufacturer_button(game, width, height)
        
        # Draw instruction text or warning
        self._draw_instructions(game, width, height, all_cars_balanced, in_active_race)
        
    def _draw_upgrades_panel(self, game, width, height):
        """Draw the upgrades panel on the customization screen"""
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
        upgrade_description = "Permanent upgrades boost performance"
        upgrade_desc_text = self.font.render(upgrade_description, True, (220, 220, 255))
        self.screen.blit(upgrade_desc_text, (upgrade_panel_rect.x + 20, upgrade_panel_rect.y + 60))
        
        # Define permanent upgrades to display
        permanent_upgrades = [
            {"name": "Engine", "level": game.engine_upgrade_level, "description": "Improves acceleration"},
            {"name": "Tires", "level": game.tires_upgrade_level, "description": "Improves handling"},
            {"name": "Aerodynamics", "level": game.aero_upgrade_level, "description": "Improves aerodynamics"},
        ]
        
        # Draw each upgrade with level indicator and upgrade button
        y_offset = upgrade_panel_rect.y + 90
        button_width = 120
        button_height = 30
        level_bar_width = 150
        level_bar_height = 15
        
        # Store buttons info for mouse interaction
        game.upgrade_buttons = {}
        
        # Get mouse position and state
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Check if we're in an active race
        in_active_race = game.state == STATE_RACING or game.state == STATE_PAUSE
        
        # Store reference to car for upgrades
        car = game.cars[game.selected_car_index]
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
        
        y_offset += 15
        for line in balance_explanation:
            text = self.font.render(line, True, (180, 180, 255))
            self.screen.blit(text, (upgrade_panel_rect.x + 20, y_offset))
            y_offset += 25

    def _draw_manufacturer_button(self, game, width, height):
        """draw the manufacturer selector button"""
        button_width = 155
        button_height = 45
        game.manufacturer_button_rect = pygame.Rect(
            width//2 + width//7.5 - button_width//2,
            height - 320,
            button_width,
            button_height
        )
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        # Check if mouse is over button
        button_hovered = game.manufacturer_button_rect.collidepoint(mouse_pos)
        # Button background with pulsing effect
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        # Button is enabled
        button_bg_color = (0, int(pulse * 0.7), int(pulse)) if button_hovered else (0, 0, int(pulse))
        button_border_color = BLUE if not button_hovered else (0, 0, 240)
        button_text_color = WHITE
        pygame.draw.rect(self.screen, button_bg_color, game.manufacturer_button_rect)
        pygame.draw.rect(self.screen, button_border_color, game.manufacturer_button_rect, 3, border_radius=10)
        # Button text
        button_text = "SELECT MANUFACTURER"
        button_surface = pygame.font.Font(None, 17).render(button_text, True, button_text_color)
        button_text_pos = (
            game.manufacturer_button_rect.centerx - button_surface.get_width()//2,
            game.manufacturer_button_rect.centery - button_surface.get_height()//2
        )
        
        self.screen.blit(button_surface, button_text_pos)
        
    def _draw_race_button(self, game, width, height, all_cars_balanced, in_active_race):
        """Draw the start race button at the bottom of the screen"""
        button_width = 300
        button_height = 70
        game.start_race_button_rect = pygame.Rect(
            width//2 - button_width//2,
            height - 120,
            button_width,
            button_height
        )
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if mouse is over button
        button_hovered = game.start_race_button_rect.collidepoint(mouse_pos) and not in_active_race
        
        # Button background with pulsing effect - disable if balance is not correct or in active race
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 50 + 100
        if all_cars_balanced and not in_active_race:
            # Button is enabled
            button_bg_color = (0, int(pulse * 0.7), int(pulse)) if button_hovered else (0, 0, int(pulse))
            button_border_color = WHITE if not button_hovered else (250, 250, 250)
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
        
    def _draw_instructions(self, game, width, height, all_cars_balanced, in_active_race):
        """Draw instruction text or warning messages"""
        # Draw race status message if we're in a race
        if in_active_race:
            status_text = "Race in progress - Setup changes locked"
            status_surface = self.font.render(status_text, True, (255, 200, 100))
            self.screen.blit(status_surface, (width//2 - status_surface.get_width()//2, height - 200))
            
            status_text2 = "Press ESC to end race and return to this menu"
            status_surface2 = self.font.render(status_text2, True, (200, 200, 200))
            self.screen.blit(status_surface2, (width//2 - status_surface2.get_width()//2, height - 180))
        
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