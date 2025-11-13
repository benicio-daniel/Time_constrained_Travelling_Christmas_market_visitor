import random
class Ant:
    def __init__(self, opening_at, closing_at, travel_time, 
                 start_market, start_time, stay_time=30, time_limit=2300, DNA=None, mutation=1, generation=0):
        # Surrounding context
        self.opening_at = opening_at
        self.closing_at = closing_at
        self.travel_time = travel_time
        self.time_limit = time_limit

        # Initial setup for the ant
        self.start_market = start_market
        self.start_time = start_time
        self.current_market = start_market
        self.current_time = start_time
        self.stay_time = stay_time
        self.DNA = DNA
        self.mutation = mutation
        self.generation = generation

        # Ant's journey tracking
        self.visited = [start_market]
        self.path = [(start_market, start_time)]

    def evaluate_possibilities(self):
        # Time when the ant would leave the current market
        self.current_time += self.stay_time
        if self.current_time > self.time_limit:  # Exceeds overall time limit
                return []
        
        options = []

        # Get all neighboring markets and travel times from the current one
        neighbors = self.travel_time[self.current_market]

        for dest, travel_time in neighbors.items():
            # Skip if this market has already been visited
            if dest in self.visited:
                continue

            # Calculate time to arrive, opening and closing at the destination market
            arrival_time = self.current_time + travel_time
            open_time = self.opening_at[dest]
            close_time = self.closing_at[dest]

            # Check time constraints
            if arrival_time < open_time:             # Arrive before opening
                continue
            if self.current_time > close_time:       # Leave after closing
                continue

            # Collect valid options
            options.append((dest, travel_time))

        # Return all possible next markets that the ant can move to
        return options

    def move(self):
        options = self.evaluate_possibilities()
        if not options:
            return False  # No valid moves available
        
        # Choose one destination (here randomly; later you could add heuristics)
        if self.mutation == 1:
            next_market, travel_time = random.choice(options)
        elif self.mutation == 2:
            # here we add the DNA values to influence the choice
            pass # Placeholder for another selection strategy

        # Update ant's state
        self.current_time += travel_time
        self.current_market = next_market
        self.visited.append(next_market)
        self.path.append((next_market, self.current_time))

        return True  # Move was successful
    
    def breed(self):
        # Create a new ant with the same parameters
        new_DNA = self.path.copy() # add gene manipulation logic
        return Ant(
            # passes surrounding context
            opening_at=self.opening_at,
            closing_at=self.closing_at,
            travel_time=self.travel_time,
            time_limit=self.time_limit,

            # passes initial setup
            start_market=self.start_market,
            start_time=self.start_time,
            stay_time=self.stay_time,
            DNA=new_DNA,
            mutation=self.mutation,
            generation=self.generation + 1
        )