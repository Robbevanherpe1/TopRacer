from tracks.constants import EMPTY, TRACK, TRACKSIDE, WALL, PIT, CAR_SPAWN, CAR_SPAWN_POINT

class BaseTrack:
    def __init__(self, track):
        self.track = track
        
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
        
        # If no CAR_SPAWN found, try PIT
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == PIT:
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
        
        # If still no spawns found, use PIT with small offsets
        if not spawn_positions:
            finish_pos = None
            for y in range(self.track.grid_height):
                for x in range(self.track.grid_width):
                    if self.track.grid[y][x] == PIT:
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
                tile_type == PIT or
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
    
    def get_lane_waypoint_position(self, index, lane):
        """Get the position of a waypoint in a specific lane"""
        waypoints = {
            'center': self.track.waypoints,
            'left': self.track.waypoints_left,
            'right': self.track.waypoints_right
        }
        
        # Make sure we have valid waypoints for the requested lane
        if lane not in waypoints or not waypoints[lane]:
            # Fall back to center lane if requested lane doesn't exist
            lane = 'center'
            
        # Ensure index is valid
        if 0 <= index < len(waypoints[lane]):
            waypoint = waypoints[lane][index]
            return (waypoint[0] * self.track.tile_size + self.track.tile_size // 2, 
                   waypoint[1] * self.track.tile_size + self.track.tile_size // 2)
        
        # Default to the start position if the index is invalid
        return self.get_start_position()
        
    def get_waypoint_position(self, index, use_pit_road=False, lane='center'):
        """Return the world coordinates for a specific waypoint, with pit road and lane options"""
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
        
        # If not using pit road or not a pit road waypoint, use the specified lane
        return self.get_lane_waypoint_position(index, lane)




