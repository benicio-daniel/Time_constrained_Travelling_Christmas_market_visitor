import random
from google_maps import GoogleMaps
from ant import Ant
from ant_colony import Ant_Colony

class AntOptimizer:
    def __init__(self, 
                 maps_service_objekt,
                 num_colonies=10, 
                 ants_per_colony=20,
                 stay_time=30,
                 time_limit=2300,
                 initial_DNA=None,
                 generation=0,
                 mutation=1
                 ):
        """
        Initialises an AntOptimizer object with the given parameters.

        Args:
            maps (GoogleMaps): The Google Maps service object.
            markets (list): A list of all available markets.
            num_colonies (int, optional): The number of ant colonies. Defaults to 10.
            ants_per_colony (int, optional): The number of ants in each colony. Defaults to 20.
        """

        self.maps = maps_service_objekt

        self.num_colonies = num_colonies
        self.ants_per_colony = ants_per_colony

        self.stay_time = stay_time
        self.time_limit = time_limit
        self.initial_DNA = initial_DNA
        self.generation = generation
        self.mutation = mutation

        self.colonies = []  # list of AntColonies

    def initialize_colonies(self, all_markets, open_times):
        """
        Initializes the colonies with random starting positions.

        Args:
            all_markets (list): A list of all available markets.
            open_times (list): A list of opening times for each market.
        """

        for _ in range(self.num_colonies):

            # choose random index
            idx = random.randrange(len(all_markets))

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
                mutation=self.mutation
            )

            self.colonies.append(colony)


    def run_one_generation(self):
        """
        Run one generation of the algorithm.

        Move all ants in all colonies one step forward and update the pheromone map.

        Returns:
            None
        """

        paths = []

        for colony in self.colonies:
            path = colony.move_ants()
            paths.append(path)
        
        self.maps.update_pheromones(paths)