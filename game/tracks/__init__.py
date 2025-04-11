from tracks.constants import EMPTY, TRACK, WALL, FINISH_LINE, TRACKSIDE, CAR_SPAWN, CAR_SPAWN_POINT
from tracks.base_track import BaseTrack
from tracks.draw_track import DrawTrack
from tracks.one_track import Track1

class Track:
    def __init__(self, csv_path='game/tracks/csv/track1_2.csv'):
        self.tile_size = 40  # Increased from 30 to 40
        self.base_track = BaseTrack(self)
        self.draw_track = DrawTrack(self)
        self.track1 = Track1(self)
        
        # Pre-load textures
        self.load_textures()
        self.load_from_csv(csv_path)
        self.define_waypoints()
        # Initialize pit road waypoints
        self.define_pit_road_waypoints()
        # Flag to enable/disable pit road
        self.use_pit_road = False
        
        # Add left and right track lanes (alternates to main waypoints)
        self.waypoints_left = []
        self.waypoints_right = []
        # Create the alternate lanes
        self.create_alternate_lanes()
    
    def create_alternate_lanes(self):
        """Create left and right lane alternatives to the main waypoints"""
        if not self.waypoints:
            return
            
        # Define an offset for the alternate lanes (perpendicular to track direction)
        lane_offset = 1  # 1 tile offset
        
        # Clear existing alternate lanes
        self.waypoints_left = []
        self.waypoints_right = []
        
        # For each waypoint, create left and right alternates
        for i in range(len(self.waypoints)):
            current_wp = self.waypoints[i]
            next_wp_idx = (i + 1) % len(self.waypoints)
            next_wp = self.waypoints[next_wp_idx]
            
            # Calculate direction vector between waypoints
            dx = next_wp[0] - current_wp[0]
            dy = next_wp[1] - current_wp[1]
            
            # Normalize the direction vector
            length = (dx**2 + dy**2)**0.5
            if length > 0:
                dx, dy = dx / length, dy / length
            
            # Calculate perpendicular vectors for left and right lanes
            # Left is 90° counterclockwise, right is 90° clockwise
            left_dx, left_dy = -dy, dx
            right_dx, right_dy = dy, -dx
            
            # Create offset waypoints
            left_wp = (current_wp[0] + left_dx * lane_offset, current_wp[1] + left_dy * lane_offset)
            right_wp = (current_wp[0] + right_dx * lane_offset, current_wp[1] + right_dy * lane_offset)
            
            # Add to alternate lanes
            self.waypoints_left.append(left_wp)
            self.waypoints_right.append(right_wp)
        
        print(f"Created {len(self.waypoints_left)} left lane waypoints and {len(self.waypoints_right)} right lane waypoints")

    ## waitpoints track

    def define_waypoints(self):
        """Define waypoints based on the track layout"""
        self.track1.define_waypoints()
        
    def define_pit_road_waypoints(self):
        """Define pit road waypoints that connect from waypoints"""
        self.track1.define_pit_road_waypoints()
        
    
    ## Drawing track

    def load_textures(self):
        """Load and prepare all textures used for the track tiles"""
        self.draw_track.load_textures()
        
    def load_from_csv(self, csv_path):
        """Load track data from a CSV file"""
        self.draw_track.load_from_csv(csv_path)

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw the track with camera offset applied"""
        self.draw_track.draw(surface, camera_x, camera_y)
        
    def draw_waypoints(self, surface, camera_x=0, camera_y=0):
        """Draw the waypoints on the track for debugging/visualization"""
        self.draw_track.draw_waypoints(surface, camera_x, camera_y)


    ## Track properties
        
    def get_start_position(self):
        """Return the starting position coordinates for cars"""
        return self.base_track.get_start_position()
    
    def get_all_spawn_positions(self):
        """Return all car spawn positions for multiple cars"""
        return self.base_track.get_all_spawn_positions()
        
    def get_tile_at(self, x, y):
        """Get the tile type at the given pixel coordinates"""
        return self.base_track.get_tile_at(x, y)
    
    def get_closest_waypoint(self, pos):
        """Get the index of the closest waypoint to a given position"""
        return self.base_track.get_closest_waypoint(pos)

    def get_waypoint_position(self, index, use_pit_road=False, lane='center'):
        """Return the world coordinates for a specific waypoint, with pit road option and lane selection"""
        return self.base_track.get_waypoint_position(index, use_pit_road, lane)
    
    def is_wall(self, x, y):
        """Check if the given coordinates are in a wall or out of bounds"""
        return self.base_track.is_wall(x, y)
    
    def is_actual_wall(self, x, y):
        """Stricter check for walls that only returns True for actual walls"""
        return self.base_track.is_actual_wall(x, y)
    
    def is_track(self, x, y):
        """Check if the given tile is part of the track"""
        return self.base_track.is_track(x, y)
        
    def get_tile_type_at(self, x, y):
        """Get the type of tile at given coordinates"""
        return self.base_track.get_tile_type_at(x, y)
    
    def is_strict_wall(self, x, y):
        """Very strict wall check - only returns True for actual wall tiles"""
        return self.base_track.is_strict_wall(x, y)



