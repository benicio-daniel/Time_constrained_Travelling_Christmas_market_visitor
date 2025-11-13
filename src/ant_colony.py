class Ant_Colony:
    def __init__(self, ants):
        # Idea we have different colonies each starting at the same position 
        # Through different colonies we can evaluate 
        # These live through generations and performe selection and breeding
        pass

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