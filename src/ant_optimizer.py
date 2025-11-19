class AntOptimizer:
    def __init__(self, data):
        self.data = data    
    
    def inter_colony_comparision(self, colonies):
        # Compare different ant colonies based on their performance
        pass

    def intra_colony_evaluation(self, colony):
        # Evaluate ants within a single colony
        pass

    def phases_of_evaluation(self, phase):
        # Different phases of evaluation for the ants
        if phase == 1:
            # find eg 50% best starting markets
            pass
        if phase == 2:
            # use DNA to find best routes
            # to etablish good local search
            # set startign pheromones
            pass 
        if phase == 3:
            # sporn new ant at random positions with best DNA (fixed)
            # use pheromone maps to guide ants (with decay?)
            # over many days
            pass

    def die_out_weak_ants(self, colony):
        # Remove ants that performed poorly
        pass

"""
    class ColonyEvaluator:
    def __init__(self, colonies):
        self.colonies = colonies

    def run_simulation(self):
        # 1. LASS ALLE AMEISEN ALLER KOLONIEN LAUFEN
        for colony in self.colonies:
            for ant in colony.ants:
                while ant.move():
                    pass

        # 2. EVALUIERE JEDE KOLONIE EINZELN
        for colony in self.colonies:
            colony.evaluate_fitness()
            colony.selection()
            colony.breed_new_generation()"""