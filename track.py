import pygame

# Define tile types
EMPTY = 0  # No tile
TRACK = 1  # Gray asphalt
WALL = 2   # Red wall
START = 3  # Starting position (special track tile)

# Colors
GRAY = (80, 80, 80)  # Asphalt
RED = (255, 0, 0)    # Wall
GREEN = (0, 155, 0)  # Start line
BLACK = (0, 0, 0)    # Empty space

# Map tile to color
TILE_COLORS = {
    EMPTY: BLACK,
    TRACK: GRAY,
    WALL: RED,
    START: GREEN
}

class Track:
    def __init__(self):
        # Create a bigger oval track
        # 0 = empty, 1 = track, 2 = wall, 3 = start
        self.grid = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0],
            [0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 1, 1, 1, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 1, 1, 1, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 1, 1, 1, 1, 1, 2, 0, 0, 0, 0],
            [0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0],
            [0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.tile_size = 40  # Increased from 30 to 40
        self.width = len(self.grid[0])
        self.height = len(self.grid)
        
        # Enhanced waypoints for optimal racing line - increased from 8 to 24 for smooth navigation
        self.waypoints = [
            # Start/finish straight
            (13, 22),  # Start line
            (15, 22),  # Mid start straight
            (19, 22),  # Approaching turn 1
            
            # Turn 1 (bottom right)
            (21, 20),  # Entry of turn 1
            (22, 18),  # Apex of turn 1
            (24, 15),  # Exit of turn 1
            
            # Right side straight
            (24, 13),  # Mid right straight
            (24, 11),  # Approaching turn 2
            
            # Turn 2 (top right)
            (24, 9),   # Entry of turn 2
            (22, 6),   # Apex of turn 2
            (18, 4),   # Exit of turn 2
            
            # Top straight
            (15, 3),   # Mid top straight  
            (12, 3),   # Approaching turn 3
            
            # Turn 3 (top left)
            (8, 4),    # Entry of turn 3 
            (5, 6),    # Apex of turn 3 /14
            (3, 9),    # Exit of turn 3
            
            # Left side straight
            (3, 11),   # Mid left straight
            (3, 14),   # Approaching turn 4
            
            # Turn 4 (bottom left)
            (4, 17),   # Entry of turn 4
            (6, 19),   # Mid turn 4
            (8, 21),   # Apex of turn 4
            
            # Bottom straight
            (10, 22),  # Exit of turn 4
            (11, 22),  # Approaching finish line
            (12, 22),  # Before start line
        ]
        
    def get_start_position(self):
        """Return the starting position coordinates for cars"""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == START:
                    return x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2
        # Default position if START not found
        return 3 * self.tile_size, 13 * self.tile_size
        
    def get_tile_at(self, x, y):
        """Get the tile type at the given pixel coordinates"""
        # Ensure coordinates are integers when used as grid indices
        grid_x = int(x // self.tile_size)
        grid_y = int(y // self.tile_size)
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.grid[grid_y][grid_x]
        return WALL  # Return wall for out of bounds
        
    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the track on the given surface with camera offset"""
        # Calculate visible area based on camera position
        screen_width, screen_height = surface.get_size()
        start_x = max(0, int(camera_x // self.tile_size))
        start_y = max(0, int(camera_y // self.tile_size))
        end_x = min(self.width, int((camera_x + screen_width) // self.tile_size) + 1)
        end_y = min(self.height, int((camera_y + screen_height) // self.tile_size) + 1)
        
        # Only draw visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.grid[y][x]
                if tile_type != EMPTY:  # Only draw non-empty tiles
                    color = TILE_COLORS[tile_type]
                    rect = pygame.Rect(x * self.tile_size - camera_x, y * self.tile_size - camera_y, 
                                       self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, color, rect)
                    
                    # Draw a border for better visibility
                    pygame.draw.rect(surface, (50, 50, 50), rect, 1)
    
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
            
            # Draw waypoint number
            font = pygame.font.SysFont(None, 20)
            number_text = font.render(str(i), True, (0, 0, 0))
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