from tracks.constants import FINISH_LINE, TRACK

class Track1:
    def __init__(self, track):
        self.track = track
        
    def define_waypoints(self):
        """Define waypoints based on the track layout"""
        # Reset existing waypoints
        self.track.waypoints = []
        
        # Find the start line (usually marked by FINISH_LINE type)
        start_x, start_y = None, None
        
        # Look for the starting position (Finish line tile)
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == FINISH_LINE:
                    start_x, start_y = x, y
                    break
            if start_x is not None:
                break
        
        # If no finish line is found, try to find the first track tile
        if start_x is None:
            for y in range(self.track.grid_height):
                for x in range(self.track.grid_width):
                    if self.track.grid[y][x] == TRACK:
                        start_x, start_y = x, y
                        break
                if start_x is not None:
                    break
        
        # If we still don't have a starting point, use a default
        if start_x is None:
            start_x, start_y = self.track.grid_width // 2, self.track.grid_height // 2
        
        # Add waypoints around the track by following the track tiles
        # This is a simplified approach - a more sophisticated algorithm
        # would trace the racing line
        self.track.waypoints = [
            # Add start point
            (start_x + 12, start_y - 1),  # 0
            
            # For now, hardcode some waypoints for the track in track1.csv
            # These should be adjusted based on the actual track layout
            (start_x + 15, start_y - 1),  # 1
            (start_x + 20, start_y - 1),  # 2
            (start_x + 24, start_y),      # 3
            (start_x + 26, start_y + 4),  # 4
            (start_x + 27, start_y + 10), # 5
            (start_x + 31, start_y + 12), # 6
            (start_x + 36, start_y + 10), # 7
            (start_x + 40, start_y + 4),  # 8
            (start_x + 40, start_y - 2),  # 9
            (start_x + 35, start_y - 7),  # 10
            (start_x + 30, start_y - 10), # 11
            (start_x + 26, start_y - 14), # 12
            (start_x + 24, start_y - 19), # 13
            (start_x + 20, start_y - 23), # 14
            (start_x + 13, start_y - 23), # 15   
            (start_x + 10, start_y - 28), # 16
            (start_x + 7, start_y - 31),  # 17
            (start_x + 1, start_y - 33),  # 18
            (start_x - 16, start_y - 33), # 19
            (start_x - 18, start_y - 30), # 20
            (start_x - 16, start_y - 27), # 21
            (start_x - 12, start_y - 25), # 22
            (start_x - 6, start_y - 24),  # 23
            (start_x + 7, start_y - 16),  # 24
            (start_x + 7, start_y - 12),  # 25
            (start_x + 7, start_y - 7),   # 26
            (start_x + 5, start_y - 5),   # 27
            (start_x + 1, start_y - 7),   # 28
            (start_x + 0, start_y - 4),   # 29  
            (start_x + 3, start_y - 1),   # 30
        ]
        
        print(f"Defined {len(self.track.waypoints)} waypoints")
    
    def define_pit_road_waypoints(self):
        """Define pit road waypoints that connect from the second last waypoint (29) to the 5th waypoint (5)"""
        # Find the start line coordinates to use as reference like in define_waypoints
        start_x, start_y = None, None
        
        # Look for the starting position (Finish line tile)
        for y in range(self.track.grid_height):
            for x in range(self.track.grid_width):
                if self.track.grid[y][x] == FINISH_LINE:
                    start_x, start_y = x, y
                    break
            if start_x is not None:
                break
        
        # If no finish line is found, use the default from the waypoints
        if start_x is None and len(self.track.waypoints) > 0:
            # Extract start_x and start_y from first waypoint
            first_waypoint = self.track.waypoints[0]
            start_x = first_waypoint[0] - 12  # Reverse the offset from define_waypoints
            start_y = first_waypoint[1] + 1   # Reverse the offset from define_waypoints
        
        # If we still don't have a starting point, use a default
        if start_x is None:
            start_x, start_y = self.track.grid_width // 2, self.track.grid_height // 2
        
        # Create pit road waypoints that connect waypoint 29 to waypoint 5
        # These are custom points that form a pit road path
        self.track.pit_road_waypoints = [
            # Start from waypoint 29 - second last waypoint
            (start_x + 1, start_y - 2),    # Starting point (same as waypoint 29)
            (start_x + 1, start_y),        # Move left into pit entrance
            (start_x + 3, start_y + 2),    # Continue along pit lane
            (start_x + 5, start_y + 3),    # Turn downward
            (start_x + 10, start_y + 3),   # Continue pit lane
            (start_x + 15, start_y + 3),   # Continue pit lane
            (start_x + 20, start_y + 3),   # Turn towards exit
            (start_x + 23, start_y + 2),   # Continue towards pit exit
            (start_x + 26, start_y + 4),   # Continue turning
            (start_x + 27, start_y + 10),  # End at waypoint 5
        ]
        
        print(f"Defined {len(self.track.pit_road_waypoints)} pit road waypoints")
