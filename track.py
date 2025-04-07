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
        # Create a simple oval track
        # 0 = empty, 1 = track, 2 = wall, 3 = start
        self.grid = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
            [0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0],
            [0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0],
            [0, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 1, 2, 2, 0, 0, 0, 0, 2, 2, 1, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 1, 1, 2, 0, 0, 0],
            [0, 2, 1, 1, 1, 2, 2, 0, 0, 0, 0, 2, 2, 1, 1, 1, 2, 0, 0, 0],
            [0, 2, 3, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 0, 0, 0],
            [0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0],
            [0, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 0, 0, 0, 0],
            [0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        self.tile_size = 30
        self.width = len(self.grid[0])
        self.height = len(self.grid)
        
        # Define waypoints for AI to follow (x, y) coordinates
        self.waypoints = [
            (3, 13),  # Start line
            (6, 3),   # Top straightaway
            (13, 3),  # Top right corner
            (16, 8),  # Right side
            (16, 13), # Bottom right corner 
            (13, 15), # Bottom straightaway
            (6, 15),  # Bottom left corner
            (3, 8),   # Left side, back to start
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
        
    def draw(self, surface):
        """Draw the track on the given surface"""
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.grid[y][x]
                if tile_type != EMPTY:  # Only draw non-empty tiles
                    color = TILE_COLORS[tile_type]
                    rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                       self.tile_size, self.tile_size)
                    pygame.draw.rect(surface, color, rect)
                    
                    # Draw a border for better visibility
                    pygame.draw.rect(surface, (50, 50, 50), rect, 1)
    
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