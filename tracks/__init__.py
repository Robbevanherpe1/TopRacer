from tracks.base_track import BaseTrack
from tracks.one_track import Track1


class Track:
    def __init__(self, csv_path='tracks/csv/track1_2.csv'):
        self.tile_size = 40
        self.load_texture = BaseTrack(self)
        self.load_from_csv = BaseTrack(self, csv_path)
        self.define_waypoints = Track1(self)

    
    def load_textures(self):
        """Draw the start screen - delegated to start screen UI"""
        self.base_track.load_texture(self)

    def load_from_csv(self,csv_path):
        """Load track data from a CSV file"""
        self.base_track.load_from_csv(self, csv_path)

    def define_waypoints(self):
        """Define waypoints based on the track layout"""
        self.track1.define_waypoints(self)
    
   

