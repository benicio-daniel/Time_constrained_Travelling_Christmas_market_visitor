import random
from google_maps import GoogleMaps
from ant import Ant
from ant_colony import Ant_Colony
from ant_optimizer import Ant_Optimizer


"""here happends the magic WOW!!!!!!"""

phase = None

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

'''
Phase 1 = exploration
Phase 2 = exploitation
Phase 3 = respawn
50 beste Startmärkte auswählt
Mutation anpasst
Pheromone korrekt integriert
'''