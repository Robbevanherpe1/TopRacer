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
CAR_SPAWN = 9  # This is the same as finish line in the map
CAR_SPAWN_POINT = 10  # New constant for actual car spawn points

class Track:
    def __init__(self, csv_path='tracks/csv/track1_2.csv'):
        self.tile_size = 40  # Increased from 30 to 40
        # Pre-load textures
        self.load_textures()
        self.load_from_csv(csv_path)
        self.define_waypoints()
        # Initialize pit road waypoints
        self.define_pit_road_waypoints()
        # Flag to enable/disable pit road
        self.use_pit_road = False
        
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
            (start_x + 12, start_y - 1),#0
            
            # For now, hardcode some waypoints for the track in track1.csv
            # These should be adjusted based on the actual track layout
            (start_x + 15, start_y -1),#1
            (start_x + 20, start_y -1),#2
            (start_x + 24, start_y ),#3
            (start_x + 26, start_y + 4),#4
            (start_x + 27, start_y + 10),#5
            (start_x + 31, start_y + 12),#6
            (start_x + 36, start_y + 10),#7
            (start_x + 40, start_y + 4),#8
            (start_x + 40, start_y - 2),#9
            (start_x + 35, start_y - 7),#10
            (start_x + 30, start_y - 10),#11
            (start_x + 26, start_y - 14),#12
            (start_x + 24, start_y - 19),#13
            (start_x + 20, start_y - 23),#14
            (start_x + 13, start_y - 23),#15   
            (start_x + 10, start_y - 28),#16
            (start_x + 7, start_y - 31),#17
            (start_x + 1, start_y - 33),#18
            (start_x - 16, start_y - 33),#19
            (start_x - 18, start_y - 30),#20
            (start_x - 16, start_y - 27),#21
            (start_x - 12, start_y - 25),#22
            (start_x - 6, start_y - 24),#23
            (start_x + 7, start_y - 16),#24
            (start_x + 7, start_y - 12),#25
            (start_x + 7, start_y - 7),#26
            (start_x + 5, start_y - 5),#27
            (start_x +1, start_y - 7),#28
            (start_x + 0, start_y - 4),#29  
            (start_x + 3, start_y - 1),#30
        ]
        
        print(f"Defined {len(self.waypoints)} waypoints")
    
    def define_pit_road_waypoints(self):
        """Define pit road waypoints that connect from the second last waypoint (29) to the 5th waypoint (5)"""
        # Find the start line coordinates to use as reference like in define_waypoints
        start_x, start_y = None, None
        
        # Look for the starting position (Finish line tile)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == FINISH_LINE:
                    start_x, start_y = x, y
                    break
            if start_x is not None:
                break
        
        # If no finish line is found, use the default from the waypoints
        if start_x is None and len(self.waypoints) > 0:
            # Extract start_x and start_y from first waypoint
            first_waypoint = self.waypoints[0]
            start_x = first_waypoint[0] - 12  # Reverse the offset from define_waypoints
            start_y = first_waypoint[1] + 1   # Reverse the offset from define_waypoints
        
        # If we still don't have a starting point, use a default
        if start_x is None:
            start_x, start_y = self.grid_width // 2, self.grid_height // 2
        
        # Create pit road waypoints that connect waypoint 29 to waypoint 5
        # These are custom points that form a pit road path
        self.pit_road_waypoints = [
            # Start from waypoint 29 - second last waypoint
            (start_x + 1, start_y - 2),  # Starting point (same as waypoint 29)
            (start_x + 1, start_y),  # Move left into pit entrance
            (start_x + 3, start_y +2), # Continue along pit lane
            (start_x + 5, start_y + 3), # Turn downward
            (start_x + 10, start_y + 3), # Continue pit lane
            (start_x + 15, start_y + 3),  # Continue pit lane
            (start_x + 20, start_y + 3), # Turn towards exit
            (start_x + 23, start_y + 2),# Continue towards pit exit
            (start_x + 26, start_y + 4), # Continue turning
            (start_x + 27, start_y + 10),# End at waypoint 5
        ]
        
        print(f"Defined {len(self.pit_road_waypoints)} pit road waypoints")
    
    def is_wall(self, x, y):
        """Check if the given tile is a wall"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return True  # Out of bounds is considered a wall
        
        # Check if the tile is a wall
        # Explicitly exclude CAR_SPAWN (9) and CAR_SPAWN_POINT (10) from being walls
        try:
            tile_type = self.grid[grid_y][grid_x]
            return (tile_type == WALL or tile_type == EMPTY) and tile_type != CAR_SPAWN and tile_type != CAR_SPAWN_POINT
        except IndexError:
            # If we're out of bounds in the grid, consider it a wall
            return True
    
    def is_actual_wall(self, x, y):
        """Stricter check that only returns True for actual walls, not track boundaries"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return True  # Out of bounds is considered a wall
        
        try:
            tile_type = self.grid[grid_y][grid_x]
            # ONLY consider actual WALL tiles as walls, not empty or track sides
            return tile_type == WALL
        except IndexError:
            # If we're out of bounds in the grid, consider it a wall
            return True
    
    def is_track(self, x, y):
        """Check if the given tile is part of the track"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return False  # Out of bounds is not track
        
        # Check if the tile is track or finish line
        # Also consider CAR_SPAWN and CAR_SPAWN_POINT as part of the track
        tile_type = self.grid[grid_y][grid_x]
        return (tile_type == TRACK or 
                tile_type == FINISH_LINE or
                tile_type == TRACKSIDE or
                tile_type == CAR_SPAWN or
                tile_type == CAR_SPAWN_POINT)
    
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
                     # Draw trackside using pre-loaded texture
                    if TRACKSIDE in self.tile_textures and self.tile_textures[TRACKSIDE]:
                        surface.blit(self.tile_textures[TRACKSIDE], (screen_x, screen_y))
                    else:
                        # Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (50, 150, 50), 
                                        (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == TRACK:
                    # Draw track using pre-loaded texture
                    if TRACK in self.tile_textures and self.tile_textures[TRACK]:
                        surface.blit(self.tile_textures[TRACK], (screen_x, screen_y))
                    else:
                        # Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (80, 80, 80), 
                                        (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == WALL:
                    # Draw wall using pre-loaded texture
                    if WALL in self.tile_textures and self.tile_textures[WALL]:
                        surface.blit(self.tile_textures[WALL], (screen_x, screen_y))
                    else:
                        # Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (150, 150, 150), 
                                        (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == FINISH_LINE:
                    # Draw finish line
                    pygame.draw.rect(surface, (200, 200, 50), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == TRACKSIDE:
                    # Draw trackside (grass)# Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (50, 150, 50), 
                                      (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == CAR_SPAWN:
                    # Draw regular finish line (same as finish line)
                    pygame.draw.rect(surface, (200, 200, 50), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                elif tile_type == CAR_SPAWN_POINT:
                    # Draw car spawn point (bright blue)
                    pygame.draw.rect(surface, (100, 200, 255), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
                else:
                    # Draw unknown tile type (default to dark grey)
                    pygame.draw.rect(surface, (50, 50, 50), 
                                    (screen_x, screen_y, self.tile_size, self.tile_size))
        
        # Add debug visualization for collision detection
        if hasattr(self, 'debug_collisions') and self.debug_collisions:
            for point in self.debug_collisions:
                x, y, is_wall = point
                color = (255, 0, 0) if is_wall else (0, 255, 0)
                pygame.draw.circle(surface, color, (int(x - camera_x), int(y - camera_y)), 3)
            
            # Clear after drawing
            self.debug_collisions = []
    
    def get_start_position(self):
        """Return the starting position coordinates for cars"""
        # First look for CAR_SPAWN_POINT tile (10)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == CAR_SPAWN_POINT:
                    return x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2
        
        # If no CAR_SPAWN_POINT found, try CAR_SPAWN
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == CAR_SPAWN:
                    return x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2
        
        # If no CAR_SPAWN found, try FINISH_LINE
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == FINISH_LINE:
                    return x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2
        
        # Default position if nothing found
        return 3 * self.tile_size, 13 * self.tile_size
    
    def get_all_spawn_positions(self):
        """Return all car spawn positions for multiple cars"""
        spawn_positions = []
        
        # First collect all CAR_SPAWN_POINT tiles (10)
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == CAR_SPAWN_POINT:
                    pos = (x * self.tile_size + self.tile_size // 2, 
                           y * self.tile_size + self.tile_size // 2)
                    spawn_positions.append(pos)
        
        # If no CAR_SPAWN_POINT found, try CAR_SPAWN tiles (9)
        if not spawn_positions:
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid[y][x] == CAR_SPAWN:
                        pos = (x * self.tile_size + self.tile_size // 2, 
                               y * self.tile_size + self.tile_size // 2)
                        spawn_positions.append(pos)
        
        # If still no spawns found, use FINISH_LINE with small offsets
        if not spawn_positions:
            finish_pos = None
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if self.grid[y][x] == FINISH_LINE:
                        finish_pos = (x * self.tile_size + self.tile_size // 2, 
                                      y * self.tile_size + self.tile_size // 2)
                        break
                if finish_pos:
                    break
            
            if finish_pos:
                # Create multiple spawn positions around the finish line
                finish_x, finish_y = finish_pos
                offsets = [(0, 0), (-20, 0), (20, 0), (0, -20), (0, 20)]
                for offset_x, offset_y in offsets:
                    spawn_positions.append((finish_x + offset_x, finish_y + offset_y))
            else:
                # Default position if nothing found
                spawn_positions.append((3 * self.tile_size, 13 * self.tile_size))
        
        return spawn_positions
        
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
        pit_waypoint_color = (255, 0, 0)  # Red for pit waypoints
        pit_connection_color = (200, 0, 200)  # Purple for pit connections
        
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
        
        # Draw pit road waypoints if they exist
        if hasattr(self, 'pit_road_waypoints') and self.pit_road_waypoints:
            # Draw connections between pit road waypoints
            for i in range(len(self.pit_road_waypoints) - 1):
                current_wp = self.pit_road_waypoints[i]
                next_wp = self.pit_road_waypoints[i + 1]
                
                # Calculate screen positions with camera offset
                current_x = current_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
                current_y = current_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
                next_x = next_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
                next_y = next_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
                
                # Draw a line connecting the pit waypoints
                pygame.draw.line(surface, pit_connection_color, (current_x, current_y), (next_x, next_y), 2)
            
            # Draw each pit waypoint
            for i, waypoint in enumerate(self.pit_road_waypoints):
                # Calculate screen position with camera offset
                screen_x = waypoint[0] * self.tile_size + self.tile_size // 2 - camera_x
                screen_y = waypoint[1] * self.tile_size + self.tile_size // 2 - camera_y
                
                # Draw pit waypoint circle in different color
                pygame.draw.circle(surface, pit_waypoint_color, (screen_x, screen_y), 5)
                
                # Draw pit waypoint number
                waypoint_font = pygame.font.Font(None, 18)
                number_text = waypoint_font.render(f"P{i}", True, (0, 0, 0))
                number_rect = number_text.get_rect(center=(screen_x, screen_y))
                surface.blit(number_text, number_rect)
            
            # Draw connections between main track and pit road
            # Connect waypoint 29 (second last) to first pit waypoint
            if len(self.waypoints) > 29 and len(self.pit_road_waypoints) > 0:
                # Start of pit road
                main_wp = self.waypoints[29]
                pit_wp = self.pit_road_waypoints[0]
                
                main_x = main_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
                main_y = main_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
                pit_x = pit_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
                pit_y = pit_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
                
                pygame.draw.line(surface, pit_connection_color, (main_x, main_y), (pit_x, pit_y), 2)
                
                # End of pit road
                main_wp = self.waypoints[5]
                pit_wp = self.pit_road_waypoints[-1]
                
                main_x = main_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
                main_y = main_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
                pit_x = pit_wp[0] * self.tile_size + self.tile_size // 2 - camera_x
                pit_y = pit_wp[1] * self.tile_size + self.tile_size // 2 - camera_y
                
                pygame.draw.line(surface, pit_connection_color, (pit_x, pit_y), (main_x, main_y), 2)
    
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

    def get_waypoint_position(self, index, use_pit_road=False):
        """Return the world coordinates for a specific waypoint, with pit road option"""
        # Check if we're using the pit road and requesting a waypoint that would be replaced by it
        if use_pit_road and hasattr(self, 'use_pit_road') and self.use_pit_road:
            # If we're between waypoints 29 and 5
            if index == 30 or index == 0 or (index >= 1 and index <= 5):
                # Calculate the corresponding pit road waypoint
                if index == 30:
                    pit_index = 0  # Start of pit road
                elif index == 0:
                    pit_index = 2  # Middle of pit entrance  
                elif index >= 1 and index <= 4:
                    # Distribute the remaining waypoints along the pit road
                    pit_index = 3 + index
                else:  # index == 5
                    pit_index = len(self.pit_road_waypoints) - 1  # End of pit road
                
                # Make sure the pit index is valid
                pit_index = min(pit_index, len(self.pit_road_waypoints) - 1)
                
                waypoint = self.pit_road_waypoints[pit_index]
                return (waypoint[0] * self.tile_size + self.tile_size // 2,
                        waypoint[1] * self.tile_size + self.tile_size // 2)
        
        # Regular waypoint handling
        if 0 <= index < len(self.waypoints):
            waypoint = self.waypoints[index]
            return (waypoint[0] * self.tile_size + self.tile_size // 2, 
                    waypoint[1] * self.tile_size + self.tile_size // 2)
        
        # Default to start position if waypoint index is invalid
        return self.get_start_position()
    
    def get_tile_type_at(self, x, y):
        """Get the type of tile at given coordinates"""
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return -1  # Out of bounds
        
        try:
            return self.grid[grid_y][grid_x]
        except IndexError:
            return -1
    
    def is_wall(self, x, y):
        """Check if the given coordinates are in a wall or out of bounds"""
        # Original implementation - too sensitive
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return True  # Out of bounds is considered a wall
        
        # Check if the tile is a wall
        try:
            tile_type = self.grid[grid_y][grid_x]
            return tile_type == WALL
        except IndexError:
            return True
    
    def is_actual_wall(self, x, y):
        """More lenient check for walls that only returns True for actual walls"""
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return True  # Out of bounds is considered a wall
        
        try:
            tile_type = self.grid[grid_y][grid_x]
            # Only consider WALL (0) as a wall, nothing else
            return tile_type == WALL
        except IndexError:
            return True
    
    def is_strict_wall(self, x, y):
        """Very strict wall check - only returns True for actual wall tiles"""
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        # Check bounds with margin
        if grid_x < 0 or grid_x >= self.grid_width or grid_y < 0 or grid_y >= self.grid_height:
            return True  # Out of bounds is wall
        
        try:
            # Only WALL (0) is considered a wall, with an exact match
            return self.grid[grid_y][grid_x] == WALL
        except IndexError:
            return True