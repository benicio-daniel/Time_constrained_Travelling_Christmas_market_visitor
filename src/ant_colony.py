import random
from google_maps import GoogleMaps
from ant import Ant

class Ant_Colony:
    def __init__(
        self,
        maps_service_objekt,
        number_of_ants,
        start_market=None,  # have to be initialized
        start_time=None,    # have to be initialized
        stay_time=30,
        time_limit=2300,
        initial_DNA=None,
        generation=0,
        mutation=1
    ):
        """
        Initialises an Ant_Colony object with the given parameters.

        Args:
            maps_service_objekt (GoogleMaps): The Google Maps service object.
            number_of_ants (int): The number of ants in the colony.
            start_market (str, optional): The starting market of the ants. Defaults to None.
            start_time (datetime, optional): The starting time of the ants. Defaults to None.
            stay_time (int, optional): The time the ants spend at each market. Defaults to 30.
            time_limit (int, optional): The overall time limit for the ants. Defaults to 2300.
            initial_DNA (list, optional): The initial DNA of the ants. Defaults to None.
            generation (int, optional): The generation of the ants. Defaults to 0.
            mutation (int, optional): The mutation type of the ants. Defaults to 1.

        Attributes:
            maps (GoogleMaps): The Google Maps service object.
            number_of_ants (int): The number of ants in the colony.
            start_market (str): The starting market of the ants.
            start_time (datetime): The starting time of the ants.
            stay_time (int): The time the ants spend at each market.
            time_limit (int): The overall time limit for the ants.
            initial_DNA (list): The initial DNA of the ants.
            generation (int): The generation of the ants.
            mutation (int): The mutation type of the ants.
            ants (list): A list of all the ants in the colony.
            fitness_scores (dict): A dictionary containing the fitness scores of the ants.
        """

        self.maps = maps_service_objekt
        self.number_of_ants = number_of_ants
        self.start_market = start_market
        self.start_time = start_time
        self.stay_time = stay_time
        self.time_limit = time_limit
        self.initial_DNA = initial_DNA or []
        self.generation = generation
        self.mutation = mutation

        # all the ants in this colony
        self.ants = []

        # spawn initial ants
        self.spawn_ants()

    def spawn_ants(self):
        """
        Resets the list of ants and spawns a new set of ants.

        The new ants are given the same parameters as the old ants, but with a new DNA, which is a copy of the initial DNA.

        The new ants are then added to the list of ants.
        
        """

        self.ants = [] # reset for new ants

        for i in range(self.number_of_ants):
            
            ant = Ant(
                maps_service_objekt=self.maps,
                start_market=self.start_market,
                start_time=self.start_time,
                stay_time=self.stay_time,
                time_limit=self.time_limit,
                DNA=self.initial_DNA.copy(),
                generation=self.generation,
                mutation=self.mutation,
            )

            self.ants.append(ant)
    
    def fitness(self, ant):
        """
        Calculates the fitness of an ant.

        The fitness is calculated as the number of markets visited multiplied by 100, minus the current time of the ant.

        Args:
            ant (Ant): The ant to calculate the fitness for.

        Returns:
            int: The fitness of the ant.
        """
        # if same length prefer the one with less time used -> (simple fitness function, may be improved)
        return len(ant.visited) * 100 - ant.current_time

    def selection(self, survival_rate=0.2):

        # Fitness of all ants
        scored_ants = [(ant, self.fitness(ant)) for ant in self.ants]
        fitness_values = [score for (_, score) in scored_ants]

        # Fitness can be negative, shift to positive values (for roulette wheel)
        min_f = min(fitness_values)
        if min_f < 0:
            # shift all fitness values so minimum becomes 1
            fitness_values = [f - min_f + 1 for f in fitness_values]

        # determine number of survivors
        num_survivors = max(2, int(len(self.ants) * survival_rate))

        # Selection by roulette wheel
        survivors = random.choices(
            self.ants,
            weights=fitness_values,
            k=num_survivors
        )

        return survivors
    
    def mutate_dna(self, dna1, dna2):
        """
        Mutates the DNA of two parents by performing a crossover operation.

        Args:
            dna1 (list): The DNA of the first parent.
            dna2 (list): The DNA of the second parent.

        Returns:
            list: The mutated DNA.
        """

        # Crossover (simple one-point crossover, may be improved)
        point_of_crossover = random.randint(0, min(len(dna1)-1, len(dna2)-1))
        return dna1[:point_of_crossover] + dna2[point_of_crossover:]
    
    def breed(self, parent1, parent2):
        """
        Breeds a new ant by performing a crossover operation on the DNA of two parent ants.

        The crossover operation is performed by taking the DNA of the two parent ants and
        swapping them at a random point. The resulting DNA is then used to create a new ant.

        Args:
            parent1 (Ant): The first parent ant.
            parent2 (Ant): The second parent ant.

        Returns:
            Ant: The new ant resulting from the crossover operation.
        """
        
        # Extract path without times
        dna1 = [m for (m, _) in parent1.path]
        dna2 = [m for (m, _) in parent2.path]

        # Perform mutation / crossover
        new_dna = self.mutate_dna(dna1, dna2)

        child = Ant(
            maps_service_objekt=self.maps,
            start_market=self.start_market, # should this be random from parents?
            start_time=self.start_time,
            stay_time=self.stay_time,
            time_limit=self.time_limit,
            DNA=new_dna,
            generation=self.generation + 1,
            mutation=self.mutation,
        )

        return child

    def next_generation(self):
        """
        Advances the generation of the Ant Colony by one step.

        Selects ants based on their fitness and breeds new ants by performing crossover operations on the selected ants.
        The resulting new ants replace the old ants in the AntColony.

        Returns:
            None
        """

        # sourvivors
        survivors = self.selection()
        new_ants = []

        # breeding
        while len(new_ants) < self.number_of_ants:
            parent1, parent2 = random.sample(survivors, 2)
            child = self.breed(parent1, parent2)
            new_ants.append(child)

        self.ants = new_ants
        self.generation += 1

    def move_ants(self):
        """
        Move all ants in the AntColony one step forward.

        For each ant, move it to the next market until it can no longer move.
        Then, advance the generation by one step and replace the old ants with the new ones.

        Returns:
            None
        """

        paths = []

        for ant in self.ants:
            while ant.move():
                pass
            paths.append((ant.path, self.fitness(ant)))
        
        self.ants = self.next_generation()

        return paths