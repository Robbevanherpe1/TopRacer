import pygame
from constants.constants import *

class BaseUI:
    """Base UI class with shared functionality for all UI components"""
    
    def __init__(self, screen):
        self.screen = screen
        
        # Initialize local font objects that won't be affected by module import issues
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)