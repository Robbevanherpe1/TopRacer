import csv
import pygame
from track import EMPTY, TRACK, TRACKSIDE, WALL

class BaseTrack:

    def load_textures(self):
        """Load and prepare all textures used for the track tiles"""
        # Create a dictionary to store all tile textures
        self.tile_textures = {}
        
        # Load grass texture for trackside
        try:
            grass_img = pygame.image.load('assets/grass.png')
            asfalt_img = pygame.image.load('assets/asphalt.png')
            tirewall_img = pygame.image.load('assets/tirewall.png')
            # Scale the image to fit the tile size
            self.tile_textures[TRACKSIDE] = pygame.transform.scale(grass_img, (self.tile_size, self.tile_size))
            self.tile_textures[TRACK] = pygame.transform.scale(asfalt_img, (self.tile_size, self.tile_size))
            self.tile_textures[WALL] = pygame.transform.scale(tirewall_img, (self.tile_size, self.tile_size))
        except pygame.error:
            print("Warning: Could not load texture, using color instead")
            self.tile_textures[TRACKSIDE] = None
            self.tile_textures[TRACK] = None
            self.tile_textures[WALL] = None
        # You can add more textures here for other tile types

    def load_from_csv(self, csv_path):
        """Load track data from a CSV file"""
        self.grid = []
        
        try:
            with open(csv_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    # Convert string values to integers
                    int_row = [int(cell) for cell in row]
                    self.grid.append(int_row)
                
            # Store grid dimensions for later use
            self.grid_height = len(self.grid)
            self.grid_width = len(self.grid[0]) if self.grid_height > 0 else 0
            
            print(f"Loaded track with dimensions: {self.grid_width}x{self.grid_height}")
        except Exception as e:
            print(f"Error loading track from CSV: {e}")
            # Create a default small grid if loading fails
            self.grid = [[EMPTY for _ in range(20)] for _ in range(20)]
            self.grid_height = 20
            self.grid_width = 20
        
    


        