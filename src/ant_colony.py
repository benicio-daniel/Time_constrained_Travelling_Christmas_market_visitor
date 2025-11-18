import random
from google_maps import GoogleMaps

class Ant_Colony:
    def __init__(
        self,
        maps_service_objekt,
        number_of_ants,
        start_market=None,
        stay_time=30,
        time_limit=2300,
        mutation=1,
        initial_DNA=None,
        generation=0
    ):
        self.maps = maps_service_objekt
        self.number_of_ants = number_of_ants
        self.start_market = start_market
        self.stay_time = stay_time
        self.time_limit = time_limit
        self.mutation = mutation
        self.generation = generation
        self.initial_DNA = initial_DNA or []

        # Enthalten alle Ameisen dieser Kolonie
        self.ants = []

        # Zur Auswertung
        self.fitness_scores = {}

        # Spawne Ameisen
        self.spawn_ants()

    def spawn_ants(self):
        self.ants = []  # Reset für neue Generation

        # Liste aller möglichen Startmärkte aus Maps
        all_markets = self.maps.get_all_markets()

        for i in range(self.number_of_ants):

            if self.start_market is None:
                # Phase 2: random Startmarkt
                start = random.choice(all_markets)
            else:
                # Phase 1: alle starten am selben Ort
                start = self.start_market

            # Startzeit könnte fix oder random sein
            start_time = self.maps.get_default_start_time(start)

            ant = Ant(
                maps_service_objekt=self.maps,
                start_market=start,
                start_time=start_time,
                stay_time=self.stay_time,
                time_limit=self.time_limit,
                DNA=self.initial_DNA.copy(),
                mutation=self.mutation,
                generation=self.generation
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