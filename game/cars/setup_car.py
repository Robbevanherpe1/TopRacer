import random


class SetupCar:
    # Define manufacturer-specific bonuses (values from -0.1 to +0.1)
    MANUFACTURER_BONUSES = {
        # Ferrari: Excellent engine, good aero, average handling, weaker brakes
        "Ferrari": {"Engine": 0.09, "Aerodynamics": 0.06, "Handling": 0.0, "Brakes": -0.05, "Tires": -0.04},
        
        # Bentley: Good brakes and comfort (handling), weaker acceleration
        "Bentley": {"Engine": -0.05, "Aerodynamics": 0.02, "Handling": 0.08, "Brakes": 0.07, "Tires": -0.02},
        
        # BMW: Balanced with better handling and brakes
        "BMW": {"Engine": 0.02, "Aerodynamics": 0.0, "Handling": 0.06, "Brakes": 0.05, "Tires": -0.02},
        
        # McLaren: Excellent aero and good engine
        "McLaren": {"Engine": 0.05, "Aerodynamics": 0.09, "Handling": 0.03, "Brakes": -0.02, "Tires": -0.03},
        
        # Mercedes: Good engine, balanced overall
        "Mercedes": {"Engine": 0.07, "Aerodynamics": 0.02, "Handling": 0.03, "Brakes": 0.0, "Tires": -0.02},
        
        # Nissan: Great tires, decent engine, weaker aero
        "Nissan": {"Engine": 0.04, "Aerodynamics": -0.05, "Handling": 0.0, "Brakes": 0.02, "Tires": 0.08},
        
        # Porsche: Great handling and brakes, decent aero
        "Porsche": {"Engine": 0.0, "Aerodynamics": 0.04, "Handling": 0.08, "Brakes": 0.05, "Tires": -0.03},
        
        # Renault: Best tires, weaker engine
        "Renault": {"Engine": -0.03, "Aerodynamics": -0.02, "Handling": 0.03, "Brakes": 0.0, "Tires": 0.09}
    }

    def __init__(self, car):
        self.car = car

    def update_performance_from_setup(self):
        """Calculate car performance values based on setup"""
        # Engine affects top speed and acceleration
        engine_factor = 0.8 + (self.car.setup["Engine"] / 10) * 0.4  # 0.8-1.2 range
        
        # Tires affect cornering grip
        tires_factor = 0.8 + (self.car.setup["Tires"] / 10) * 0.4  # 0.8-1.2 range
        
        # Aerodynamics affect top speed and high-speed cornering
        aero_factor = 0.8 + (self.car.setup["Aerodynamics"] / 10) * 0.4  # 0.8-1.2 range
        
        # Handling affects turn responsiveness
        handling_factor = 0.8 + (self.car.setup["Handling"] / 10) * 0.4  # 0.8-1.2 range
        
        # Brakes affect braking efficiency
        brakes_factor = 0.8 + (self.car.setup["Brakes"] / 10) * 0.4  # 0.8-1.2 range
        
        # Apply permanent upgrades if this is an engineer car and we're attached to a game
        try:
            if getattr(self.car, 'is_engineer_car', False) and hasattr(self.car, 'game') and self.car.game is not None:
                # Get car-specific upgrades - use the car's name (garage name) as the key
                garage_name = self.car.name  # Team Alpha or Team Omega
                
                # Check if car_upgrades exists and has data for this garage
                if hasattr(self.car.game, 'car_upgrades') and garage_name in self.car.game.car_upgrades:
                    # Use the specific car's upgrades
                    car_upgrades = self.car.game.car_upgrades[garage_name]
                    
                    # Apply upgrade bonuses - each upgrade level adds 0.03 to the factor (30% boost at max level 10)
                    engine_upgrade_level = car_upgrades.get('engine', 0)
                    engine_upgrade_bonus = engine_upgrade_level * 0.03
                    engine_factor += engine_upgrade_bonus
                    
                    tires_upgrade_level = car_upgrades.get('tires', 0)
                    tires_upgrade_bonus = tires_upgrade_level * 0.03
                    tires_factor += tires_upgrade_bonus
                    
                    aero_upgrade_level = car_upgrades.get('aero', 0)
                    aero_upgrade_bonus = aero_upgrade_level * 0.03
                    aero_factor += aero_upgrade_bonus
        except AttributeError:
            # If any attribute error occurs, just continue with base values
            pass
        
        # Apply manufacturer-specific bonuses
        manufacturer_bonus = SetupCar.MANUFACTURER_BONUSES.get(self.car.manufacturer, {})
        engine_factor += manufacturer_bonus.get("Engine", 0)
        tires_factor += manufacturer_bonus.get("Tires", 0)
        aero_factor += manufacturer_bonus.get("Aerodynamics", 0)
        handling_factor += manufacturer_bonus.get("Handling", 0)
        brakes_factor += manufacturer_bonus.get("Brakes", 0)
        
        # Calculate performance values
        self.car.max_speed = self.car.base_max_speed * ((engine_factor * 0.7) + (aero_factor * 0.3))
        self.car.acceleration = self.car.base_acceleration * engine_factor
        self.car.turn_speed = self.car.base_turn_speed * ((handling_factor * 0.6) + (tires_factor * 0.4))
        self.car.braking = self.car.base_braking * brakes_factor
        
    def set_random_setup(self):
        """Generate random setup values for AI cars"""
        for key in self.car.setup:
            self.car.setup[key] = random.randint(3, 8)  # Random values between 3-8
        self.update_performance_from_setup()
        
    def adjust_setup_balanced(self, key, new_value):
        """
        Adjust car setup while maintaining balance.
        When a value is increased above 5, other values are decreased proportionally.
        When a value is decreased below 5, other values are increased proportionally.
        The total sum of all setup values must remain 25 (5 stats × baseline value of 5)
        """
        # Get current value and calculate change
        old_value = self.car.setup[key]
        value_change = new_value - old_value
        
        # If no change, nothing to do
        if value_change == 0:
            return
        
        # Set the new value first
        self.car.setup[key] = new_value
        
        # Calculate how much we need to distribute to/from other stats
        points_to_distribute = -value_change  # negative because we're balancing
        
        # Get list of other keys that can be adjusted (all except the one being changed)
        other_keys = [k for k in self.car.setup.keys() if k != key]
        
        # Count how many adjustable keys we have (those not already at min or max)
        if points_to_distribute > 0:  # We need to increase other stats
            adjustable_keys = [k for k in other_keys if self.car.setup[k] < 10]
        else:  # We need to decrease other stats
            adjustable_keys = [k for k in other_keys if self.car.setup[k] > 1]
        
        # If no adjustable keys, revert the change
        if not adjustable_keys:
            self.car.setup[key] = old_value
            return
        
        # Calculate how many points to distribute to each stat
        points_per_key = points_to_distribute / len(adjustable_keys)
        
        # Apply distribution, ensuring no stat goes below 1 or above 10
        remaining_points = points_to_distribute
        for adjust_key in adjustable_keys:
            # Calculate new value with proportional adjustment
            if points_per_key > 0:  # Increasing other stats
                # How much can this stat increase?
                max_increase = 10 - self.car.setup[adjust_key]
                adjustment = min(points_per_key, max_increase)
            else:  # Decreasing other stats
                # How much can this stat decrease?
                max_decrease = self.car.setup[adjust_key] - 1
                adjustment = max(points_per_key, -max_decrease)
            
            # Apply the adjustment
            self.car.setup[adjust_key] += adjustment
            remaining_points -= adjustment
        
        # If we still have points to distribute (due to min/max limits),
        # try to distribute them among remaining adjustable keys
        if abs(remaining_points) > 0.01:  # Use a small threshold for floating point comparison
            # Recalculate adjustable keys
            if remaining_points > 0:  # We need to increase other stats more
                adjustable_keys = [k for k in other_keys if self.car.setup[k] < 10]
            else:  # We need to decrease other stats more
                adjustable_keys = [k for k in other_keys if self.car.setup[k] > 1]
            
            # Try another round of distribution if we have adjustable keys
            if adjustable_keys:
                points_per_key = remaining_points / len(adjustable_keys)
                for adjust_key in adjustable_keys:
                    # Similar logic as before
                    if points_per_key > 0:
                        max_increase = 10 - self.car.setup[adjust_key]
                        adjustment = min(points_per_key, max_increase)
                    else:
                        max_decrease = self.car.setup[adjust_key] - 1
                        adjustment = max(points_per_key, -max_decrease)
                    
                    self.car.setup[adjust_key] += adjustment
                    remaining_points -= adjustment
                    
                    # Stop if we've distributed all points
                    if abs(remaining_points) < 0.01:
                        break
            
            # If we still couldn't distribute all points, revert the original change
            if abs(remaining_points) > 0.01:
                # Revert all changes
                self.car.setup[key] = old_value
                for adjust_key in other_keys:
                    self.car.setup[adjust_key] = round(self.car.setup[adjust_key])  # Round to avoid floating point issues
                return
        
        # Round all values to integers to avoid floating point issues
        for k in self.car.setup:
            self.car.setup[k] = round(self.car.setup[k])
        
        # Update car performance based on new setup
        self.update_performance_from_setup()