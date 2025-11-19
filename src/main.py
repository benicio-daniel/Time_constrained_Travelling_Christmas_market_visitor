#maps = GoogleMaps(api_key="XYZ")
#markets = maps.load_christmas_markets()
# oder so ähnlich...


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