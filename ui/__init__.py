from ui.customization_ui import CustomizationUI
from ui.race_ui import RaceUI
from ui.race_end_ui import RaceEndUI
from ui.start_screen_ui import StartScreenUI
from ui.manufacturer_ui import ManufacturerUI

class UI:
    """Controller class that delegates to specialized UI components"""
    
    def __init__(self, screen):
        """Initialize all UI components"""
        self.screen = screen
        self.start_screen_ui = StartScreenUI(screen)
        self.race_ui = RaceUI(screen)
        self.customization_ui = CustomizationUI(screen)
        self.race_end_ui = RaceEndUI(screen)
        self.manufacturer_ui = ManufacturerUI(screen)
    
    def draw_start_screen(self, game, animation):
        """Draw the start screen - delegated to start screen UI"""
        self.start_screen_ui.draw_start_screen(game, animation)
    
    def draw_customization_screen(self, game):
        """Draw the customization screen - delegated to customization UI"""
        self.customization_ui.draw_customization_screen(game)
    
    def draw_manufacturer_selection(self, game):
        """Draw the manufacturer selection screen - delegated to manufacturer UI"""
        self.manufacturer_ui.draw_manufacturer_selection(game)
    
    def draw_race_end_screen(self, game, animation):
        """Draw the race end screen - delegated to race end UI"""
        self.race_end_ui.draw_race_end_screen(game, animation)
    
    def draw_ui(self, game):
        """Draw the main racing UI - delegated to race UI"""
        self.race_ui.draw_ui(game)
    
    def draw_position_overlay(self, game):
        """Draw the position overlay - delegated to race UI"""
        self.race_ui.draw_position_overlay(game)
