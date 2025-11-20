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
Todos: (to make it work)
- [ ] start a colony at every market available & perform some generation (only using DNA) and return best markets & pheromone for prove of concept
- [ ] time limit edit convert do minutes in decimal / what is end time? (last market closing time)
- [ ] sort repository (eg. analysis needed? maybe every py script except main in one folder (does this work then))


Todos: (Ben for better process)
- [ ] does everything makes sense?
- [ ] choose the best X% starting markets and sporn a colony each and perform training by also updating pheromones & DNA (through mutations)
- [ ] after training sporn single random ants to test results and play with parameters (only one gen therefore no DNA update)
- [ ] test for multiple days (visited markets and start position add as init parameters)
argue about:
- Phase 1 = exploration
- Phase 2 = exploitation
- Phase 3 = respawn

Optional todos:
- [ ] gene mutation / crossover and fitness function better? in ant colony class
- [ ] tune alpha, beta and gamma in ant class for pheromone/ dna weights