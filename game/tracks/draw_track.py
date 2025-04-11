import csv
import pygame
import os

from tracks.constants import CAR_SPAWN, CAR_SPAWN_POINT, EMPTY, FINISH_LINE, TRACK, TRACKSIDE, WALL


class DrawTrack:
    def __init__(self, track):
        # Store a reference to the parent Track object
        self.track = track
        self.textures = None

    def load_textures(self):
        """Load and prepare all textures used for the track tiles"""
        # Dictionary to store tile textures
        self.textures = {}

        # Load basic textures
        self.textures[EMPTY] = None
        self.textures[WALL] = pygame.image.load("game/assets/tirewall.png").convert_alpha()
        self.textures[TRACK] = pygame.image.load("game/assets/asphalt.png").convert()
        self.textures[TRACKSIDE] = pygame.image.load("game/assets/grass.png").convert()
        self.textures[FINISH_LINE] = pygame.image.load("game/assets/finishline.png").convert()
        self.textures[CAR_SPAWN] = self.textures[TRACK]  # Use track texture for car spawn points
        self.textures[CAR_SPAWN_POINT] = self.textures[TRACK]  # Use track texture for car spawn points

    def load_from_csv(self, csv_path):
        """Load track data from a CSV file"""
        # Parse CSV into a grid
        self.track.grid = []
        self.track.collision_grid = []

        if not os.path.exists(csv_path):
            print(f"Error: Track file not found at {csv_path}")
            # Create a simple default track
            self.track.grid_width = 20
            self.track.grid_height = 20
            self.track.grid = [[WALL for _ in range(self.track.grid_width)] for _ in range(self.track.grid_height)]
            for y in range(5, 15):
                for x in range(5, 15):
                    self.track.grid[y][x] = TRACK
            return

        try:
            with open(csv_path, 'r') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if row and not row[0].strip().startswith('//'):  # Skip comment lines
                        # Filter out empty strings and convert to integers
                        int_row = []
                        for cell in row:
                            if cell.strip():  # Check if the cell is not empty
                                int_row.append(int(cell.strip()))
                        if int_row:  # Only add non-empty rows
                            self.track.grid.append(int_row)

            if self.track.grid:
                self.track.grid_height = len(self.track.grid)
                self.track.grid_width = len(self.track.grid[0])
                print(f"Track loaded with dimensions: {self.track.grid_width}x{self.track.grid_height}")
            else:
                print("Warning: No valid data found in CSV file")
                self.track.grid_width = 10
                self.track.grid_height = 10
                self.track.grid = [[WALL for _ in range(self.track.grid_width)] for _ in range(self.track.grid_height)]
        except Exception as e:
            print(f"Error loading track: {e}")
            self.track.grid_width = 10
            self.track.grid_height = 10
            self.track.grid = [[WALL for _ in range(self.track.grid_width)] for _ in range(self.track.grid_height)]

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the track with camera offset applied"""
        if not self.textures:
            self.load_textures()

        # Calculate visible area in grid coordinates
        visible_left = max(0, int(camera_x / self.track.tile_size))
        visible_top = max(0, int(camera_y / self.track.tile_size))
        screen_width, screen_height = surface.get_size()
        visible_right = min(self.track.grid_width, int((camera_x + screen_width) / self.track.tile_size) + 1)
        visible_bottom = min(self.track.grid_height, int((camera_y + screen_height) / self.track.tile_size) + 1)

        # Draw visible tiles
        for y in range(visible_top, visible_bottom):
            for x in range(visible_left, visible_right):
                if 0 <= y < self.track.grid_height and 0 <= x < self.track.grid_width:
                    tile = self.track.grid[y][x]
                    if tile == EMPTY or tile not in self.textures:
                        continue  # Skip empty tiles or unknown tile types
                    
                    # Calculate screen coordinates with camera offset
                    screen_x = x * self.track.tile_size - camera_x
                    screen_y = y * self.track.tile_size - camera_y
                    
                    # Draw the tile
                    texture = self.textures[tile]
                    if texture:
                        # Scale the texture if needed
                        if texture.get_width() != self.track.tile_size or texture.get_height() != self.track.tile_size:
                            texture = pygame.transform.scale(texture, (self.track.tile_size, self.track.tile_size))
                        surface.blit(texture, (screen_x, screen_y))
                    else:
                        # Draw a colored rectangle for tiles without a texture
                        color = (0, 0, 0) if tile == EMPTY else (128, 128, 128)
                        pygame.draw.rect(surface, color, pygame.Rect(screen_x, screen_y, self.track.tile_size, self.track.tile_size))

        # Draw collision debug visualization if enabled
        if hasattr(self.track, 'debug_collisions') and self.track.debug_collisions:
            for point in self.track.debug_collisions:
                x, y, tile_type = point
                color = (255, 0, 0)  # Red for collisions
                if tile_type == 1:  # Track
                    color = (0, 255, 0)  # Green for track
                elif tile_type == 3:  # Trackside
                    color = (255, 255, 0)  # Yellow for trackside
                pygame.draw.circle(surface, color, (x - camera_x, y - camera_y), 3)

    def draw_waypoints(self, surface, camera_x=0, camera_y=0):
        """Draw the waypoints on the track for debugging/visualization"""
        # Colors to use for waypoints
        waypoint_color = (255, 255, 0)  # Yellow for center lane
        left_waypoint_color = (255, 100, 100)  # Reddish for left lane
        right_waypoint_color = (100, 100, 255)  # Bluish for right lane
        connection_color = (0, 200, 200)  # Cyan
        left_connection_color = (200, 0, 0)  # Red
        right_connection_color = (0, 0, 200)  # Blue
        pit_waypoint_color = (255, 0, 0)  # Red for pit waypoints
        pit_connection_color = (200, 0, 200)  # Purple for pit connections
        
        # Draw connections for alternate lane waypoints first
        # Left lane connections
        if self.track.waypoints_left:
            for i in range(len(self.track.waypoints_left)):
                current_wp = self.track.waypoints_left[i]
                next_wp = self.track.waypoints_left[(i + 1) % len(self.track.waypoints_left)]
                
                # Calculate screen positions with camera offset
                current_x = current_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                current_y = current_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                next_x = next_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                next_y = next_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                # Draw a line connecting the waypoints
                pygame.draw.line(surface, left_connection_color, (current_x, current_y), (next_x, next_y), 2)
                
        # Right lane connections
        if self.track.waypoints_right:
            for i in range(len(self.track.waypoints_right)):
                current_wp = self.track.waypoints_right[i]
                next_wp = self.track.waypoints_right[(i + 1) % len(self.track.waypoints_right)]
                
                # Calculate screen positions with camera offset
                current_x = current_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                current_y = current_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                next_x = next_wp[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                next_y = next_wp[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                # Draw a line connecting the waypoints
                pygame.draw.line(surface, right_connection_color, (current_x, current_y), (next_x, next_y), 2)
        
        # First draw connections between waypoints for center lane
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
            
        # Draw left lane waypoints
        if self.track.waypoints_left:
            for i, waypoint in enumerate(self.track.waypoints_left):
                # Calculate screen position with camera offset
                screen_x = waypoint[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                screen_y = waypoint[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                # Draw waypoint circle
                pygame.draw.circle(surface, left_waypoint_color, (screen_x, screen_y), 4)
                
        # Draw right lane waypoints
        if self.track.waypoints_right:
            for i, waypoint in enumerate(self.track.waypoints_right):
                # Calculate screen position with camera offset
                screen_x = waypoint[0] * self.track.tile_size + self.track.tile_size // 2 - camera_x
                screen_y = waypoint[1] * self.track.tile_size + self.track.tile_size // 2 - camera_y
                
                # Draw waypoint circle
                pygame.draw.circle(surface, right_waypoint_color, (screen_x, screen_y), 4)
        
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
                
                pygame.draw.line(surface, pit_connection_color, (main_x, main_y), (pit_x, pit_y), 2)
