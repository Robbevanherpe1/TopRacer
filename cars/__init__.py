import random
import pygame

from cars.base_car import BaseCar
from cars.collision_car import CollisionCar
from cars.position_car import PositionCar
from cars.setup_car import SetupCar


class Car:

    AVAILABLE_MANUFACTURERS = [
        "Ferrari", "Bentley", "BMW", "McLaren", 
        "Mercedes", "Nissan", "Porsche", "Renault"
    ]
    

    def __init__(self, track, position=None, color=(0, 0, 255), name="Player", manufacturer="Ferrari"):
        self.track = track
        self.name = name
        self.color = color
        
        # Select random manufacturer for AI cars (not player or engineer cars)
        if "AI Car" in name and manufacturer == "Ferrari":
            self.manufacturer = random.choice(Car.AVAILABLE_MANUFACTURERS)
        else:
            self.manufacturer = manufacturer
        
        # Set starting position
        if position:
            self.x, self.y = position
        else:
            self.x, self.y = track.get_start_position()
            
        # Set safer starting position offsets that avoid walls
        self.x += random.randint(-5, 5)
        self.y += random.randint(-5, 5)
        
        # Set initial angle to face the right direction towards first waypoint
        self.angle = 0  # Will be updated in initialize_car_direction()
        self.initialize_car_direction()
        
        # Car setup properties (values from 1-10)
        self.setup = {
            "Engine": 5,     # Affects top speed and acceleration
            "Tires": 5,      # Affects cornering and grip
            "Aerodynamics": 5, # Affects top speed and cornering at high speed
            "Handling": 5,   # Affects responsiveness in corners
            "Brakes": 5      # Affects braking efficiency
        }
        
        # Car physics properties - will be modified by setup
        self.base_max_speed = 6.0
        self.base_acceleration = 0.15
        self.base_turn_speed = 3.5
        self.base_braking = 2.0
        
        # Actual performance values (calculated from base + setup)
        self.max_speed = self.base_max_speed
        self.acceleration = self.base_acceleration
        self.turn_speed = self.base_turn_speed
        self.braking = self.base_braking
        
        # Initialize speed
        self.speed = 0
        
        # Car dimensions - explicitly defined early
        self.width = 14  # Reduced from 20
        self.height = 7  # Reduced from 10
        
        # Racing properties
        self.current_waypoint = 0
        self.laps = 0
        self.lap_times = []
        self.best_lap = None
        self.last_lap_time = 0
        self.lap_start_time = pygame.time.get_ticks()
        
        # Add pit road flag - cars will take the pit road on lap 3
        self.take_pit_road = False
        self.pit_road_lap = 3  # Hardcoded to take pit road on lap 3
        self.pit_road_debug_printed = False  # Debug flag to track pit road messages
        
        # Race engineer commands
        self.push_mode = False
        self.push_remaining = 0
        self.can_push = True
        
        # Flag to identify cars controlled by the racing engineer - explicitly set this early
        self.is_engineer_car = False
        if name in ["Team Alpha", "Team Omega"]:
            self.is_engineer_car = True
        
        # Reference to game object for upgrades
        self.game = None
        
        
        # Driver characteristics
        self.skill_level = random.uniform(0.8, 1.2)  # Affects driving precision
        self.aggression = random.uniform(0.7, 1.3)   # Affects speed in corners
        
        # Load car sprite based on manufacturer
        self.update_manufacturer(self.manufacturer)
        
        # Calculate initial performance from setup
        self.update_performance_from_setup()

        
        # Add path planning variables
        self.avoidance_angle = 0
        self.avoidance_counter = 0
        self.last_obstacle_check = pygame.time.get_ticks()
        self.obstacle_check_interval = 50  # Reduced from 100 - check more frequently
        
        # Add logging and debug properties
        self.debug_mode = False
        self.waypoint_detection_multiplier = 1.5  # More forgiving waypoint detection


        self.base_car = BaseCar(self)
        self.setup_car = SetupCar(self)
        self.position_car = PositionCar(self)
        self.collision_car = CollisionCar(self)
        

    ##base

    def toggle_push_mode(self):
        self.base_car.toggle_push_mode()
            
    def draw(self, surface, camera_x=0, camera_y=0):
        self.base_car.draw(surface, camera_x, camera_y)
      
    def get_status(self):
        self.base_car.get_status()

    def update_manufacturer(self, manufacturer):
        self.base_car.update_manufacturer(manufacturer)
    
    ## position
    
    def initialize_car_direction(self):
        self.position_car.initialize_car_direction()

    def update(self, dt):
        self.position_car.update(dt)
    
    ##collisons

    def check_collision(self):
        self.collision_car.check_collision()
        
    def get_corners(self):
        self.collision_car.get_corners()

    ## setup
       
    def update_performance_from_setup(self):
        self.setup_car.update_performance_from_setup()
      
    def set_random_setup(self):
        self.setup_car.set_random_setup()
        
    def adjust_setup_balanced(self, key, new_value):
        self.setup_car.adjust_setup_balanced(key, new_value)
       

    
       