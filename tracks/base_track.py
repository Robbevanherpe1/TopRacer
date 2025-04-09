import csv
import pygame
from tracks.constants import EMPTY, TRACK, TRACKSIDE, WALL, FINISH_LINE, CAR_SPAWN, CAR_SPAWN_POINT

class BaseTrack:
    def __init__(self, track):
        self.track = track
        
    def load_textures(self):
        """Load and prepare all textures used for the track tiles"""
        # Create a dictionary to store all tile textures
        self.track.tile_textures = {}
        
        # Load grass texture for trackside
        try:
            grass_img = pygame.image.load('assets/grass.png')
            asfalt_img = pygame.image.load('assets/asphalt.png')
            tirewall_img = pygame.image.load('assets/tirewall.png')
            # Scale the image to fit the tile size
            self.track.tile_textures[TRACKSIDE] = pygame.transform.scale(grass_img, (self.track.tile_size, self.track.tile_size))
            self.track.tile_textures[TRACK] = pygame.transform.scale(asfalt_img, (self.track.tile_size, self.track.tile_size))
            self.track.tile_textures[WALL] = pygame.transform.scale(tirewall_img, (self.track.tile_size, self.track.tile_size))
        except pygame.error:
            print("Warning: Could not load texture, using color instead")
            self.track.tile_textures[TRACKSIDE] = None
            self.track.tile_textures[TRACK] = None
            self.track.tile_textures[WALL] = None

    def load_from_csv(self, csv_path):
        """Load track data from a CSV file"""
        self.track.grid = []
        
        try:
            with open(csv_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    # Convert string values to integers
                    int_row = [int(cell) for cell in row]
                    self.track.grid.append(int_row)
                
            # Store grid dimensions for later use
            self.track.grid_height = len(self.track.grid)
            self.track.grid_width = len(self.track.grid[0]) if self.track.grid_height > 0 else 0
            
            print(f"Loaded track with dimensions: {self.track.grid_width}x{self.track.grid_height}")
        except Exception as e:
            print(f"Error loading track from CSV: {e}")
            # Create a default small grid if loading fails
            self.track.grid = [[EMPTY for _ in range(20)] for _ in range(20)]
            self.track.grid_height = 20
            self.track.grid_width = 20

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the track with camera offset applied"""
        # Only render the visible part of the grid
        view_width = surface.get_width()
        view_height = surface.get_height()
        
        # Calculate the visible grid cells
        start_x = max(0, int(camera_x // self.track.tile_size))
        end_x = min(self.track.grid_width, start_x + (view_width // self.track.tile_size) + 2)
        start_y = max(0, int(camera_y // self.track.tile_size))
        end_y = min(self.track.grid_height, start_y + (view_height // self.track.tile_size) + 2)
        
        # Draw the visible grid
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # Calculate screen position
                screen_x = x * self.track.tile_size - camera_x
                screen_y = y * self.track.tile_size - camera_y
                
                # Skip if outside view
                if (screen_x + self.track.tile_size < 0 or screen_x > view_width or
                    screen_y + self.track.tile_size < 0 or screen_y > view_height):
                    continue
                
                # Get tile type and draw accordingly
                tile_type = self.track.grid[y][x]
                
                if tile_type == EMPTY:
                    # Draw trackside using pre-loaded texture
                    if TRACKSIDE in self.track.tile_textures and self.track.tile_textures[TRACKSIDE]:
                        surface.blit(self.track.tile_textures[TRACKSIDE], (screen_x, screen_y))
                    else:
                        # Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (50, 150, 50), 
                                        (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                elif tile_type == TRACK:
                    # Draw track using pre-loaded texture
                    if TRACK in self.track.tile_textures and self.track.tile_textures[TRACK]:
                        surface.blit(self.track.tile_textures[TRACK], (screen_x, screen_y))
                    else:
                        # Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (80, 80, 80), 
                                        (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                elif tile_type == WALL:
                    # Draw wall using pre-loaded texture
                    if WALL in self.track.tile_textures and self.track.tile_textures[WALL]:
                        surface.blit(self.track.tile_textures[WALL], (screen_x, screen_y))
                    else:
                        # Fallback to colored rectangle if texture isn't loaded
                        pygame.draw.rect(surface, (150, 150, 150), 
                                        (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                elif tile_type == FINISH_LINE:
                    # Draw finish line
                    pygame.draw.rect(surface, (200, 200, 50), 
                                    (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                elif tile_type == TRACKSIDE:
                    # Draw trackside (grass)
                    pygame.draw.rect(surface, (50, 150, 50), 
                                  (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                elif tile_type == CAR_SPAWN:
                    # Draw regular finish line (same as finish line)
                    pygame.draw.rect(surface, (200, 200, 50), 
                                    (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                elif tile_type == CAR_SPAWN_POINT:
                    # Draw car spawn point (bright blue)
                    pygame.draw.rect(surface, (100, 200, 255), 
                                    (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
                else:
                    # Draw unknown tile type (default to dark grey)
                    pygame.draw.rect(surface, (50, 50, 50), 
                                    (screen_x, screen_y, self.track.tile_size, self.track.tile_size))
        
        # Add debug visualization for collision detection
        if hasattr(self.track, 'debug_collisions') and self.track.debug_collisions:
            for point in self.track.debug_collisions:
                x, y, is_wall = point
                color = (255, 0, 0) if is_wall else (0, 255, 0)
                pygame.draw.circle(surface, color, (int(x - camera_x), int(y - camera_y)), 3)
            
            # Clear after drawing
            self.track.debug_collisions = []

    def draw_waypoints(self, surface, camera_x=0, camera_y=0):
        """Draw the waypoints on the track for debugging/visualization"""
        # Colors to use for waypoints
        waypoint_color = (255, 255, 0)  # Yellow
        connection_color = (0, 200, 200)  # Cyan
        pit_waypoint_color = (255, 0, 0)  # Red for pit waypoints
        pit_connection_color = (200, 0, 200)  # Purple for pit connections
        
        # First draw connections between waypoints
        for i in range(len(self.track.waypoints)):
            # Get current and next waypoint positions
            current_wp = self.track.waypoints[i]
            next_wp = self.track.waypoints[(i + 1) % len(self.track.waypoints)]
            
            # Calculate screen positions with camera offset
            current_x = current_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
            current_y = current_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
            next_x = next_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
            next_y = next_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
            
            # Draw a line connecting the waypoints
            pygame.draw.line(surface, connection_color, (current_x, current_y), (next_x, next_y), 2)
        
        # Now draw each waypoint
        for i, waypoint in enumerate(self.track.waypoints):
            # Calculate screen position with camera offset
            screen_x = waypoint[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
            screen_y = waypoint[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
            
            # Draw waypoint circle
            pygame.draw.circle(surface, waypoint_color, (screen_x, screen_y), 6)
            
            # Create a local font object here instead of using the global one
            waypoint_font = pygame.font.Font(None, 20)
            number_text = waypoint_font.render(str(i), True, (0, 0, 0))
            number_rect = number_text.get_rect(center=(screen_x, screen_y))
            surface.blit(number_text, number_rect)
        
        # Draw pit road waypoints if they exist
        if hasattr(self.track, 'pit_road_waypoints') and self.track.pit_road_waypoints:
            # Draw connections between pit road waypoints
            for i in range(len(self.track.pit_road_waypoints) - 1):
                current_wp = self.track.pit_road_waypoints[i]
                next_wp = self.track.pit_road_waypoints[i + 1]
                
                # Calculate screen positions with camera offset
                current_x = current_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                current_y = current_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                next_x = next_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                next_y = next_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                # Draw a line connecting the pit waypoints
                pygame.draw.line(surface, pit_connection_color, (current_x, current_y), (next_x, next_y), 2)
            
            # Draw each pit waypoint
            for i, waypoint in enumerate(self.track.pit_road_waypoints):
                # Calculate screen position with camera offset
                screen_x = waypoint[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                screen_y = waypoint[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                # Draw pit waypoint circle in different color
                pygame.draw.circle(surface, pit_waypoint_color, (screen_x, screen_y), 5)
                
                # Draw pit waypoint number
                waypoint_font = pygame.font.Font(None, 18)
                number_text = waypoint_font.render(f"P{i}", True, (0, 0, 0))
                number_rect = number_text.get_rect(center=(screen_x, screen_y))
                surface.blit(number_text, number_rect)
            
            # Draw connections between main track and pit road
            # Connect waypoint 29 (second last) to first pit waypoint
            if len(self.track.waypoints) > 29 and len(self.track.pit_road_waypoints) > 0:
                # Start of pit road
                main_wp = self.track.waypoints[29]
                pit_wp = self.track.pit_road_waypoints[0]
                
                main_x = main_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                main_y = main_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                pit_x = pit_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                pit_y = pit_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                pygame.draw.line(surface, pit_connection_color, (main_x, main_y), (pit_x, pit_y), 2)
                
                # End of pit road
                main_wp = self.track.waypoints[5]
                pit_wp = self.track.pit_road_waypoints[-1]
                
                main_x = main_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                main_y = main_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                pit_x = pit_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                pit_y = pit_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                pygame.draw.line(surface, pit_connection_color, (pit_x, pit_y), (main_x, main_y), 2)

    def get_start_position(self):
        """Return the starting position coordinates for cars"""
        # First look for CAR_SPAWN_POINT tile (10)
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == CAR_SPAWN_POINT:
                    return x * self.track.tile_size + self.track.tile_size // 2, y * self.track.tile_size + self.track.tile_size // 2
        
        # If no CAR_SPAWN_POINT found, try CAR_SPAWN
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == CAR_SPAWN:
                    return x * self.track.tile_size + self.track.tile_size // 2, y * self.track.tile_size + self.track.tile_size // 2
        
        # If no CAR_SPAWN found, try FINISH_LINE
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == FINISH_LINE:
                    return x * self.track.tile_size + self.track.tile_size // 2, y * self.track.tile_size + self.track.tile_size // 2
        
        # Default position if nothing found
        return 3 * self.track.tile_size, 13 * self.track.tile_size
    
    def get_all_spawn_positions(self):
        """Return all car spawn positions for multiple cars"""
        spawn_positions = []
        
        # First collect all CAR_SPAWN_POINT tiles (10)
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == CAR_SPAWN_POINT:
                    pos = (x * self.track.tile_size + self.track.tile_size // 2, 
                           y * self.track.tile_size + self.track.tile_size // 2)
                    spawn_positions.append(pos)
        
        # If no CAR_SPAWN_POINT found, try CAR_SPAWN tiles (9)
        if not spawn_positions:
            for y in range(self.track.grid_height):
                for x in range(self.track.grid_width):
                    if self.track.grid[y][x] == CAR_SPAWN:
                        pos = (x * self.track.tile_size + self.track.tile_size // 2, 
                               y * self.track.tile_size + self.track.tile_size // 2)
                        spawn_positions.append(pos)
        
        # If still no spawns found, use FINISH_LINE with small offsets
        if not spawn_positions:
            finish_pos = None
            for y in range(self.track.grid_height):
                for x in range(self.track.grid_width):
                    if self.track.grid[y][x] == FINISH_LINE:
                        finish_pos = (x * self.track.tile_size + self.track.tile_size // 2, 
                                      y * self.track.tile_size + self.track.tile_size // 2)
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
                spawn_positions.append((3 * self.track.tile_size, 13 * self.track.tile_size))
        
        return spawn_positions

    def is_wall(self, x, y):
        """Check if the given tile is a wall"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.track.tile_size)
        grid_y = int(y // self.track.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.track.grid_width or grid_y < 0 or grid_y >= self.track.grid_height:
            return True  # Out of bounds is considered a wall
        
        # Check if the tile is a wall
        # Explicitly exclude CAR_SPAWN (9) and CAR_SPAWN_POINT (10) from being walls
        try:
            tile_type = self.track.grid[grid_y][grid_x]
            return (tile_type == WALL or tile_type == EMPTY) and tile_type != CAR_SPAWN and tile_type != CAR_SPAWN_POINT
        except IndexError:
            # If we're out of bounds in the grid, consider it a wall
            return True
            
    def is_actual_wall(self, x, y):
        """Stricter check that only returns True for actual walls, not track boundaries"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.track.tile_size)
        grid_y = int(y // self.track.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.track.grid_width or grid_y < 0 or grid_y >= self.track.grid_height:
            return True  # Out of bounds is considered a wall
        
        try:
            tile_type = self.track.grid[grid_y][grid_x]
            # ONLY consider actual WALL tiles as walls, not empty or track sides
            return tile_type == WALL
        except IndexError:
            # If we're out of bounds in the grid, consider it a wall
            return True

    def is_strict_wall(self, x, y):
        """Very strict wall check - only returns True for actual wall tiles"""
        grid_x = int(x // self.track.tile_size)
        grid_y = int(y // self.track.tile_size)
        
        # Check bounds with margin
        if grid_x < 0 or grid_x >= self.track.grid_width or grid_y < 0 or grid_y >= self.track.grid_height:
            return True  # Out of bounds is wall
        
        try:
            # Only WALL (0) is considered a wall, with an exact match
            return self.track.grid[grid_y][grid_x] == WALL
        except IndexError:
            return True
            
    def is_track(self, x, y):
        """Check if the given tile is part of the track"""
        # Convert world coordinates to grid coordinates
        grid_x = int(x // self.track.tile_size)
        grid_y = int(y // self.track.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.track.grid_width or grid_y < 0 or grid_y >= self.track.grid_height:
            return False  # Out of bounds is not track
        
        # Check if the tile is track or finish line
        # Also consider CAR_SPAWN and CAR_SPAWN_POINT as part of the track
        tile_type = self.track.grid[grid_y][grid_x]
        return (tile_type == TRACK or 
                tile_type == FINISH_LINE or
                tile_type == TRACKSIDE or
                tile_type == CAR_SPAWN or
                tile_type == CAR_SPAWN_POINT)
                
    def get_tile_at(self, x, y):
        """Get the tile type at the given pixel coordinates"""
        # Ensure coordinates are integers when used as grid indices
        grid_x = int(x // self.track.tile_size)
        grid_y = int(y // self.track.tile_size)
        
        if 0 <= grid_x < self.track.grid_width and 0 <= grid_y < self.track.grid_height:
            return self.track.grid[grid_y][grid_x]
        return WALL  # Return wall for out of bounds
        
    def get_tile_type_at(self, x, y):
        """Get the type of tile at given coordinates"""
        grid_x = int(x // self.track.tile_size)
        grid_y = int(y // self.track.tile_size)
        
        # Check bounds
        if grid_x < 0 or grid_x >= self.track.grid_width or grid_y < 0 or grid_y >= self.track.grid_height:
            return -1  # Out of bounds
        
        try:
            return self.track.grid[grid_y][grid_x]
        except IndexError:
            return -1

    def get_closest_waypoint(self, pos):
        """Get the index of the closest waypoint to a given position"""
        min_dist = float('inf')
        closest_idx = 0
        
        # Ensure pos contains integers when used for position calculation
        pos_x, pos_y = int(pos[0]), int(pos[1])
        
        for i, waypoint in enumerate(self.track.waypoints):
            waypoint_x = waypoint[0] * self.track.tile_size + self.track.tile_size // 2
            waypoint_y = waypoint[1] * self.track.tile_size + self.track.tile_size // 2
            dist = ((pos_x - waypoint_x) ** 2 + (pos_y - waypoint_y) ** 2) ** 0.5
            
            if dist < min_dist:
                min_dist = dist
                closest_idx = i
                
        return closest_idx
        
    def get_waypoint_position(self, index, use_pit_road=False):
        """Return the world coordinates for a specific waypoint, with pit road option"""
        # Check if we're using the pit road and requesting a waypoint that would be replaced by it
        if use_pit_road and hasattr(self.track, 'use_pit_road') and self.track.use_pit_road:
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
                    pit_index = len(self.track.pit_road_waypoints) - 1  # End of pit road
                
                # Make sure the pit index is valid
                pit_index = min(pit_index, len(self.track.pit_road_waypoints) - 1)
                
                waypoint = self.track.pit_road_waypoints[pit_index]
                return (waypoint[0] * self.track.tile_size + self.track.tile_size // 2,
                        waypoint[1] * self.track.tile_size + self.track.tile_size // 2)
        
        # Regular waypoint handling
        if 0 <= index < len(self.track.waypoints):
            waypoint = self.track.waypoints[index]
            return (waypoint[0] * self.track.tile_size + self.track.tile_size // 2, 
                    waypoint[1] * self.track.tile_size + self.track.tile_size // 2)
        
        # Default to start position if waypoint index is invalid
        return self.get_start_position()




