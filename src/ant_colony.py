import random
from google_maps import GoogleMaps
from ant import Ant

class Ant_Colony:
    def __init__(
        self,
        maps_service_objekt,
        number_of_ants,
        start_market=None,
        start_time=None,
        stay_time=30,
        time_limit=2300,
        initial_DNA=None,
        generation=0,
        mutation=1
    ):
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

        # store fitness scores
        self.fitness_scores = {}

        # spawn initial ants
        self.spawn_ants()

    def spawn_ants(self):
        self.ants = [] # reset for new ants

        for i in range(self.number_of_ants):
            
            # how to deal with start market and time????????????????????????????????
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

    def selection(self):
        # Performs natural selection on the ants based on their performance
        pass
    
    def breed(self):
        # Create a new ant with the same parameters
        # wir brauchen ja 2 die von selection ausgewählt sind
        new_DNA = self.path.copy() # add gene manipulation logic
        return class.Ant( # wie auch immer
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