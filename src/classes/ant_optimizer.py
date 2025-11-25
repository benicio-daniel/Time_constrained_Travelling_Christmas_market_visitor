import random
from .google_maps import GoogleMaps
from .ant import Ant
from .ant_colony import Ant_Colony

class Ant_Optimizer:
    def __init__(self, 
                 maps_service_objekt:GoogleMaps,
                 num_colonies:int=10, 
                 ants_per_colony:int=20,
                 stay_time:int=30,
                 time_limit:str="23:00", # cause latest market closes there
                 initial_DNA:list|None= None,
                 generation:int=0,
                 mutation:int=1,
                 verbose:int = 1,
                 ants_multiple_days:bool = False
                 ):


        """
        Initialises an AntOptimizer object with the given parameters.

        Args:
            maps_service_objekt (GoogleMaps): The Google Maps service object.
            num_colonies (int, optional): The number of colonies to generate. Defaults to 10.
            ants_per_colony (int, optional): The number of ants per colony. Defaults to 20.
            stay_time (int, optional): The time the ants spend at each market. Defaults to 30.
            time_limit (str, optional): The overall time limit for the ants. Defaults to "23:00".
            initial_DNA (list, optional): The initial DNA of the ants. Defaults to None.
            generation (int, optional): The generation of the ants. Defaults to 0.
            mutation (int, optional): The mutation type of the ants. Defaults to 1.
            verbose (int, optional): The verbosity of the ants. Defaults to 1.
            ants_multiple_days (bool, optional): Whether the ants can visit markets multiple times in a single day. Defaults to False.
        """
        self.maps = maps_service_objekt

        self.num_colonies = num_colonies
        self.ants_per_colony = ants_per_colony

        self.stay_time = stay_time
        self.time_limit = time_limit
        self.initial_DNA = initial_DNA
        self.generation = generation
        self.mutation = mutation
        self.verbose = verbose
        self.colonies = []  # list of AntColonies
        self.ants_multiple_days = ants_multiple_days

    def initialize_colonies(self, all_markets, open_times):
        """
        Initializes the colonies with random starting.
        If more colonies than markets are requested, the markets are distributed evenly.
        The rest (or if less colonies than markets are requested) are distributed randomly without replacement.

        Args:
            all_markets (list): A list of all available markets.
            open_times (list): A list of opening times for each market.
        """
        num_markets = len(all_markets)
        indices = []

        # gets equal distribution for all markets
        while len(indices) < self.num_colonies:
            block = list(range(num_markets))
            random.shuffle(block)
            indices.extend(block)

        # Auf richtige Länge kürzen
        indices = indices[:self.num_colonies]

        for idx in indices:           
            # aligned values
            start_market = all_markets[idx]
            start_time = open_times[idx]

            colony = Ant_Colony(
                maps_service_objekt=self.maps,
                number_of_ants=self.ants_per_colony,
                start_market=start_market,
                start_time=start_time,
                stay_time=self.stay_time,
                time_limit=self.time_limit,
                initial_DNA=self.initial_DNA,
                generation=self.generation,
                mutation=self.mutation,
                verbose = self.verbose
            )

            self.colonies.append(colony)


    def run_one_generation(self) -> list[tuple[list[tuple[str, str]], float]]:
        """
        Run one generation of the algorithm.

        Move all ants in all colonies one step forward and update the pheromone map.

        Returns:
            list: A list of paths taken by the ants in each colony.
        """

        paths = []

        for colony in self.colonies:
            path = colony.move_ants() # [(edges, cost), ...]
            paths.extend(path) # flatten
            
        
        self.maps.update_pheromones(paths)
        if self.verbose ==1:
            print(paths[0])

        return paths
    def advance_to_next_generation(self):
        for colony in self.colonies:
            colony.step_generation()
        
        self.generation += 1
    
    def set_ants_multiple_days(self):
        for colony in self.colonies:
            colony.set_multiple_days(self.ants_multiple_days)