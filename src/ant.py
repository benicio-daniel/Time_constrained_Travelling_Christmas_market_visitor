import random
from google_maps import GoogleMaps
class Ant:
    def __init__(
            self, 
            maps_service_objekt, 
            start_market, 
            start_time, 
            stay_time=30, 
            time_limit=2300, 
            DNA=None, 
            generation=0, 
            mutation=1
            ):
        # Surrounding context
        self.maps = maps_service_objekt

        # Initial setup for the ant
        self.time_limit = time_limit
        self.start_market = start_market
        self.start_time = start_time
        self.current_market = start_market
        self.current_time = start_time
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
        self.current_time += self.stay_time
        if self.current_time > self.time_limit:  # Exceeds overall time limit
            return []
        
        options = []

        # Get all neighboring markets and travel times from the current one
        neighbors = self.maps.get_destinations(self.current_market)

        for dest, (travel_time, pheromone, open_time, close_time) in neighbors.items():
            # Skip if this market has already been visited
            if dest in self.visited:
                continue

            # Calculate time to arrive, opening and closing at the destination market
            arrival_time = self.current_time + travel_time

            # Check time constraints
            if arrival_time < open_time:                         # Arrive before opening
                continue
            if arrival_time + self.stay_time > close_time:       # Leave before closing
                continue

            # Collect valid options
            options.append((dest, travel_time, pheromone))

        # Return all possible next markets that the ant can move to
        return options

    def move(self):
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
                w = (pheromone ** alpha) * ((1 / travel_time) ** beta)
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

                w = (
                    (pheromone ** alpha)
                    * ((1 / travel_time) ** beta)
                    * (dna_boost ** gamma)
                )
                weights.append(w)

            next_market, travel_time, pheromone = random.choices(
                options, weights=weights, k=1
            )[0]

        # Update ant's state
        self.current_time += travel_time
        self.current_market = next_market
        self.visited.append(next_market)
        self.path.append((next_market, self.current_time))

        return True  # Move was successful