import random
from .google_maps import GoogleMaps
from datetime import timedelta
from datetime import datetime
from datetime import time, date

class Ant:
    def __init__(
            self,
            name,
            maps_service_objekt: GoogleMaps, 
            start_market:str, 
            start_time:str, 
            stay_time:int=30, 
            time_limit:str="23:00", # cause latest market closes there
            DNA:list|None=None, 
            generation:int =0, 
            mutation:int =1,
            verbose:int = 0,
            max_days: int = 1,
            days : int = 1
            ):

        # Surrounding context
        """
        Initialises an Ant object with the given parameters.

        Args:
            name (str): The name of the ant.
            maps_service_objekt (GoogleMaps): The Google Maps service object.
            start_market (str): The starting market of the ant.
            start_time (str | time): The starting time of the ant. Can be given as a string ("HH:MM") or a datetime.time object.
            stay_time (int, optional): The time the ant spends at each market. Defaults to 30.
            time_limit (str, optional): The overall time limit for the ant. Defaults to "23:00".
            DNA (list, optional): The initial DNA of the ant. Defaults to None.
            generation (int, optional): The generation of the ants. Defaults to 0.
            mutation (int, optional): The mutation type of the ants. Defaults to 1.
            verbose (int, optional): The verbosity level of the ant. Defaults to 0.

        Attributes:
            maps (GoogleMaps): The Google Maps service object.
            name (str): The name of the ant.
            start_market (str): The starting market of the ant.
            start_time (int): The starting time of the ant in minutes.
            current_min (int): The current time of the ant in minutes.
            current_market (str): The current market of the ant.
            stay_time (int): The time the ant spends at each market.
            time_limit_min (int): The overall time limit for the ant in minutes.
            DNA (list): The DNA of the ant.
            generation (int): The generation of the ants.
            mutation (int): The mutation type of the ants.
            verbose (int): The verbosity level of the ant.
            visited (list): A list of all the markets the ant has visited.
            path (list): A list of tuples containing the market and time the ant has visited.
        """
        self.maps = maps_service_objekt

        # Initial setup for the ant
        h, m = map(int, time_limit.split(":"))
        self.time_limit_min = h*60 + m
        
        self.start_market = start_market
        if isinstance(start_time, str):
            h,m = map(int, start_time.split(":"))
            self.current_min = h*60 + m
        elif isinstance(start_time, time):
            self.current_min = start_time.hour*60 + start_time.minute
        else:
            raise ValueError("Unsupported start_time type")
        self.name = name
        self.start_time = self.current_min
        self.current_market = start_market
        self.stay_time = stay_time
        self.DNA = DNA or []
        self.generation = generation
        self.mutation = mutation

        # Ant's journey tracking
        self.visited = []
        self.visited.append(start_market)
        self.path = [(start_market, start_time)]
        self.verbose = verbose
        self.days = days
        self.max_days = max_days
    def evaluate_possibilities(self): 
        """
        Evaluates all possible next markets that the ant can move to.
        
        After moving from the current market, it checks all neighboring markets and their travel times.
        It skips markets that have already been visited and checks time constraints.
        If the ant would arrive before the market opens or leave after the market closes, it is skipped.
        
        Returns a list of tuples containing the destination market, travel time and pheromone value.
        """
        
        # Time when the ant would leave the current market
        self.current_min += self.stay_time
        if self.current_min > self.time_limit_min:  # Exceeds overall time limit
            return []
        
        options = []

        # Get all neighboring markets and travel times from the current one
        neighbors = self.maps.get_destinations(self.current_market)

        for dest, (travel_time, pheromone, open_min, close_min) in neighbors.items():
            # Skip if this market has already been visited
            if dest in self.visited:
                continue

            # Calculate time to arrive, opening and closing at the destination market
            arrival_time = self.current_min + travel_time

            # Check time constraints
            if arrival_time < open_min:                         # Arrive before opening
                continue
            if arrival_time + self.stay_time > close_min:       # Leave before closing
                continue

            # Collect valid options
            options.append((dest, travel_time, pheromone))
        # Return all possible next markets that the ant can move to
        if self.verbose == 3:
            print(f"options: {options}")
        return options

    def move(self):
        """
        Move the ant to the next market.

        Evaluates all possible next markets that the ant can move to and chooses one based on the mutation type.
        If no valid moves are available, returns False.
        Otherwise, updates the ant's state and returns True.

        Mutation types:
        1. Random choice
        2. Choice biased by DNA
        3. Choice based on feromone
        4. Choice based on feromone and DNA

        Returns:
            bool: Whether the move was successful
        """
        
        options = self.evaluate_possibilities()

        if not options:
            # Try to start a new day if there are still unvisited markets and days left
            all_markets, opening_times = self.maps.get_all_markets(visited_markets=self.visited)
            if all_markets and self.days < self.max_days:
                # Pick a new starting market for the next day
                idx = random.randrange(len(all_markets))
                new_start_market = all_markets[idx]
                new_start_time_obj = opening_times[idx]

                # Reset position and time for the new day
                self.start_market = new_start_market
                self.current_market = new_start_market
                self.current_min = new_start_time_obj.hour * 60 + new_start_time_obj.minute
                self.start_time = f"{new_start_time_obj.hour:02d}:{new_start_time_obj.minute:02d}"

                # Track new day and force pheromone-based behavior
                self.days += 1
                self.mutation = 3

                # Record the new day's starting point in the path and visited list
                self.visited.append(new_start_market)
                self.path.append((new_start_market, self.start_time))

                # Re-evaluate possible moves from the new starting point
                options = self.evaluate_possibilities()
                if not options:
                    # Even on a new day, no options – stop moving
                    return False
            else:
                # No more days or no unvisited markets left
                return False  # No valid moves available
    
        # Choose one destination
        if self.mutation == 1: # random choice
            next_market, travel_time , pheromone = random.choice(options)

        elif self.mutation == 2: # based on DNA
            # Build weights based on whether the destination is in the DNA
            weights = []
            for dest, travel_time, pheromone in options:
                dna_boost = 2 if dest in self.DNA else 1
                weights.append(dna_boost)

            # Normalize
            total = sum(weights)
            probabilities = [w / total for w in weights]

            # Choose biased by DNA
            next_market, travel_time, pheromone = random.choices(
                options, weights=probabilities, k=1
            )[0]
        elif self.mutation == 3: # based on feromone
            alpha = 1.0  # pheromone influence
            beta = 2.0   # distance influence

            weights = []
            for dest, travel_time, pheromone in options:
                # Classic ACO transition rule
                minutes = travel_time
                w = (pheromone ** alpha) * ((1 / minutes) ** beta)
                weights.append(w)

            next_market, travel_time, pheromone = random.choices(
                options, weights=weights, k=1
            )[0]
        elif self.mutation == 4: # based on feromone and DNA
            alpha = 1.0   # pheromone weight
            beta = 2.0    # distance weight
            gamma = 1.5   # DNA weight boost

            weights = []
            for dest, travel_time, pheromone in options:

                dna_boost = 2 if dest in self.DNA else 1

                minutes = travel_time
                w = (
                    (pheromone ** alpha)
                    * ((1 / minutes) ** beta)
                    * (dna_boost ** gamma)
                )
                weights.append(w)

            next_market, travel_time, pheromone = random.choices(
                options, weights=weights, k=1
            )[0]
        
        # Update ant's state
        self.current_min += travel_time
        self.old_market = self.current_market
        self.current_market = next_market
        self.visited.append(next_market)
        h = self.current_min // 60
        m = self.current_min % 60
        self.path.append((next_market, f"{h:02d}:{m:02d}"))
        if self.verbose == 3:
            print(f"{self.name}\n")
            print(f"Moved from {self.old_market} to {self.current_market} at {h:02d}:{m:02d}\n")
            print(f"Visited markets: {self.visited}\n")
            
        return True  # Move was successful
    
    def set_multiple_days(self, amount_days:int):
        """
        Set the multiple_days attribute of the Ant.

        Args:
            multiple_days (bool): Whether the Ant should move over multiple days.

        Returns:
            None
        """
        self.max_days = amount_days

if __name__ == "__main__":
    pass