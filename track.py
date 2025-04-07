import pygame
import csv
import math
import os

# Define tile type constants
EMPTY = 18
TRACK = 2
WALL = 0
FINISH_LINE = 12
TRACKSIDE = 14

class Track:
    def __init__(self, csv_path='track1.csv'):
        self.tile_size = 40  # Increased from 30 to 40
        self.load_from_csv(csv_path)
        self.define_waypoints()
        
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
    
    def define_waypoints(self):
        """Define waypoints based on the track layout"""
        # Reset existing waypoints
        self.waypoints = []
        
        # Find the start line (usually marked by FINISH_LINE type)
        start_x, start_y = None, None
        
        # Look for the starting position (Finish line tile)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == FINISH_LINE:
                    start_x, start_y = x, y
                    break
            if start_x is not None:
                break
        
        # If no finish line is found, try to find the first track tile
        if start_x is None:
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid[y][x] == TRACK:
                        start_x, start_y = x, y
                        break
                if start_x is not None:
                    break
        
        # If we still don't have a starting point, use a default
        if start_x is None:
            start_x, start_y = self.grid_width // 2, self.grid_height // 2
        
        # Add waypoints around the track by following the track tiles
        # This is a simplified approach - a more sophisticated algorithm
        # would trace the racing line
        self.waypoints = [
            # Add start point
            (start_x + 5, start_y - 1),#0
            
            # For now, hardcode some waypoints for the track in track1.csv
            # These should be adjusted based on the actual track layout
            (start_x + 10, start_y),#1
            (start_x + 15, start_y),#2
            (start_x + 24, start_y ),#3
            (start_x + 26, start_y + 4),#4
            (start_x + 27, start_y + 10),#5
            (start_x + 31, start_y + 12),#6
            (start_x + 36, start_y + 10),#7
            (start_x + 40, start_y + 4),#8
            (start_x + 40, start_y - 2),#9
            (start_x + 35, start_y - 5),#10
            (start_x + 30, start_y - 8),#11
            (start_x + 25, start_y - 14),#12
            (start_x + 24, start_y - 19),#13
            (start_x + 20, start_y - 23),#14
            (start_x + 12, start_y - 23),#15   
            (start_x + 10, start_y - 28),#16
            (start_x + 7, start_y - 31),#17
            (start_x + 1, start_y - 33),#18
            (start_x - 16, start_y - 33),#19
            (start_x - 18, start_y - 30),#20
            (start_x - 16, start_y - 27),#21
            (start_x - 12, start_y - 25),#22
            (start_x - 6, start_y - 24),#23
            (start_x + 6, start_y - 16),#24
            (start_x + 7, start_y - 12),#25
            (start_x + 7, start_y - 7),#26
            (start_x + 5, start_y - 5),#27
            (start_x + 2, start_y - 6),#28
            (start_x + 0, start_y - 3),#29  
            (start_x + 1, start_y - 2),#30
        ]
        
        print(f"Defined {len(self.waypoints)} waypoints")
    
    def is_wall(self, x, y):
        """Check if the given tile is a wall"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return True  # Out of bounds is considered a wall
        
        # Check if the tile is a wall
        return self.grid[grid_y][grid_x] == WALL or self.grid[grid_y][grid_x] == EMPTY
    
    def is_track(self, x, y):
        """Check if the given tile is part of the track"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return False  # Out of bounds is not track
        
        # Check if the tile is track or finish line
        return (self.grid[grid_y][grid_x] == TRACK or 
                self.grid[grid_y][grid_x] == FINISH_LINE or
                self.grid[grid_y][grid_x] == TRACKSIDE)
    
    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the track with camera offset applied"""
        # Only render the visible part of the grid
        view_width = surface.get_width()
        view_height = surface.get_height()
        
        # Calculate the visible grid cells
        start_x = max(0, int(camera_x // self.tile_size))
        end_x = min(self.grid_width, start_x + (view_width // self.tile_size) + 2)
        start_y = max(0, int(camera_y // self.tile_size))
        end_y = min(self.grid_height, start_y + (view_height // self.tile_size) + 2)
        
        # Draw the visible grid
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                
                # Skip if outside view
                if (screen_x + self.tile_size < 0 or screen_x > view_width or
                    screen_y + self.tile_size < 0 or screen_y > view_height):
                    continue
                
                # Get tile type and draw accordingly
                tile_type = self.grid[y][x]
                
                if tile_type == EMPTY:
                    # Draw grass/empty
                    pygame.draw.rect(surface, (50, 150, 50), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == TRACK:
                    # Draw track
                    pygame.draw.rect(surface, (80, 80, 80), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == WALL:
                    # Draw wall
                    pygame.draw.rect(surface, (150, 150, 150), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == FINISH_LINE:
                    # Draw finish line
                    pygame.draw.rect(surface, (200, 200, 50), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == TRACKSIDE:
                    # Draw trackside
                    pygame.draw.rect(surface, (120, 120, 120), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                else:
                    # Draw unknown tile type (default to dark grey)
                    pygame.draw.rect(surface, (50, 50, 50), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
    
    def get_start_position(self):
        """Return the starting position coordinates for cars"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == FINISH_LINE:
                    return x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2
        # Default position if START not found
        return 3 * self.tile_size, 13 * self.tile_size
        
    def get_tile_at(self, x, y):
        """Get the tile type at the given pixel coordinates"""
        # Ensure coordinates are integers when used as grid indices
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return self.grid[grid_y][grid_x]
        return WALL  # Return wall for out of bounds
    
    def draw_waypoints(self, surface, camera_x=0, camera_y=0):
        """Draw the waypoints on the track for debugging/visualization"""
        # Colors to use for waypoints
        waypoint_color = (255, 255, 0)  # Yellow
        connection_color = (0, 200, 200)  # Cyan
        
        # First draw connections between waypoints
        for i in range(len(self.waypoints)):
            # Get current and next waypoint positions
            current_wp = self.waypoints[i]
            next_wp = self.waypoints[(i + 1) % len(self.waypoints)]
            
            # Calculate screen positions with camera offset
            current_x = current_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
            current_y = current_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
            next_x = next_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
            next_y = next_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
            
            # Draw a line connecting the waypoints
            pygame.draw.line(surface, connection_color, (current_x, current_y), (next_x, next_y), 2)
        
        # Now draw each waypoint
        for i, waypoint in enumerate(self.waypoints):
            # Calculate screen position with camera offset
            screen_x = waypoint[0] * self.tile_size + self.tile_size // 2 - camera_x
            screen_y = waypoint[1] * self.tile_size + self.tile_size // 2 - camera_y
            
            # Draw waypoint circle
            pygame.draw.circle(surface, waypoint_color, (screen_x, screen_y), 6)
            
            # Create a local font object here instead of using the global one
            waypoint_font = pygame.font.Font(None, 20)
            number_text = waypoint_font.render(str(i), True, (0, 0, 0))
            number_rect = number_text.get_rect(center=(screen_x, screen_y))
            surface.blit(number_text, number_rect)
    
    def get_closest_waypoint(self, pos):
        """Get the index of the closest waypoint to a given position"""
        min_dist = float('inf')
        closest_idx = 0
        
        # Ensure pos contains integers when used for position calculation
        pos_x, pos_y = int(pos[0]), int(pos[1])
        
        for i, waypoint in enumerate(self.waypoints):
            waypoint_x = waypoint[0] * self.tile_size + self.tile_size // 2
            waypoint_y = waypoint[1] * self.tile_size + self.tile_size // 2
            dist = ((pos_x - waypoint_x) ** 2 + (pos_y - waypoint_y) ** 2) ** 0.5
            
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
                
        return closest_idx