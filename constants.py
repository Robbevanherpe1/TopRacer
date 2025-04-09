# Constants for TopRacer game
import pygame

# Screen dimensions
SCREEN_WIDTH = 1920  # 1080p resolution width
SCREEN_HEIGHT = 1080  # 1080p resolution height
FPS = 60

# Camera constants
CAMERA_SMOOTHNESS = 0.1  # Lower = smoother but slower camera (between 0.01 and 1.0)

# Game states
STATE_START_SCREEN = 0
STATE_CUSTOMIZATION = 1  # New state for car customization screen
STATE_RACING = 2
STATE_PAUSE = 3
STATE_RACE_END = 4  # New state for race end screen
STATE_MANUFACTURER_SELECTION = 5  # New state for manufacturer selection screen

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Set up fonts - will be initialized in main.py after pygame init
font = None
title_font = None
subtitle_font = None

def init_fonts():
    """Initialize fonts after pygame initialization"""
    global font, title_font, subtitle_font
    
    # Ensure pygame is initialized
    if not pygame.get_init():
        pygame.init()
    
    # Ensure font module is initialized
    if not pygame.font.get_init():
        pygame.font.init()
    
    # Use pygame's default font (guaranteed to work)
    font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 36)
    
    # Check that font objects were created properly
    if font is None or title_font is None or subtitle_font is None:
        raise RuntimeError("Failed to initialize fonts")