import random
from classes.google_maps import GoogleMaps
from datetime import timedelta
from datetime import datetime
from datetime import time, date

class Ant:
    def __init__(
            self, 
            maps_service_objekt, 
            start_market: str, 
            start_time: datetime, 
            stay_time=30, 
            time_limit="23:00", # cause latest market closes there
            DNA=None, 
            generation=0, 
            mutation=1
            ):

        # Surrounding context
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

        self.start_time = self.current_min
        self.current_market = start_market
        self.stay_time = stay_time
        self.DNA = DNA or []
        self.generation = generation
        self.mutation = mutation

        # Ant's journey tracking
        self.visited = [start_market]
        self.path = [(start_market, start_time)]

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
                minutes = travel_time.total_seconds() / 60
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

                minutes = travel_time.total_seconds() / 60
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
        self.current_market = next_market
        self.visited.append(next_market)
        h = self.current_min // 60
        m = self.current_min % 60
        self.path.append((next_market, f"{h:02d}:{m:02d}"))

        return True  # Move was successful