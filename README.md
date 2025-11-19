# Time_constrained_Travelling_Christmas_market_visitor
Task decription: (to be completed)
- only one day in Vienna, but want to visit as many Christmas markets as possible 
- heuristically optimise a route that maximises the amount of markets you can visit
-  e.g. walking and public transport (Wiener Linien or similar)

Further, there are the following constraints:

• At each market, you stay a predefined amount of minutes (use 30 minutes as default; make this easily configurable)

• Each market has a different opening and closing time, which are constraints on whether a market can be visited

• The overall available time is limited by the earliest opening and latest closing time

• Markets should only be visited once!

• You can assume that you start at any given market, and end at any given market, you do not care to start from e.g. your hotel/apartment :-)

• As it is impossible to visit all markets in one day, let the number of days to spend on completing the route be open. E.g. if you set 2 days, then this basically means you shall solve the fastest route for the second day with just the remaining markets. You can treat this as a simple iterative processing, you do not need to optimise the route for all days at the same time. For spanning over multiple days, let the user provide a different duration of stay at the markets for each day (simulating being less fresh on the 2ⁿᵈ and subsequent days)

You shall describe your design, coding and solution, together with an analysis of the results, in a report.

¹ So technically, this is not a travelling salesperson, as you might not be able to visit all locations, but the name for this still was chosen as very descriptive in illustrating the task to solve!

-----------------------------------------------------------
Todos: (Ben)
- [x] add travel time for public transport in csv format (see csv without secs and distance) and types (int etc.)
- [x] add opening and closing time in one csv
- [x] node reduction (for triangle inequality) -> eg. if walk time > x min then public transport etc. ??? -> reduction to one travel_time need of heuritic
- [ ] class of google maps infos (method for ant to look up, where am I, whats possible)
- [ ] pheromone logic
- [ ] function in google maps for returning every christmas market with opening time for initialisation (see load_christmas_markets in main)


Todos: (Philipp)
- [ ] Idea: 1. start at every market & perform some generation, 2. choose the best and train them (random choice whack?)
- [ ] random start positions for ants that allready exist (startzeit = öffnungszeit wo die ameise beginnt? / random start position?)
- [ ] model evaluation logic
- [ ] gene mutation / crossover and fitness function better?
- [ ] time limit edit convert do minutes in decimal / what is end time?
-> tests (wie machen wir jetzt den ganzen process? (also phasen etc.))

------------------
phases?

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