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
Todos: (Ben?)
- [ ] add travel time for public transport
- [ ] data pipline clean up (not so many notebooks etc.)
- [ ] pipline logic so that ant can evaluate data from pipline
- [ ] add opening and closing time in 2. df
- [ ] time in sec not needed?
-> addad ant_copy to play with

add:
- [ ] gene logic
- [ ] colony logic
- [ ] model evaluation logic

-> tests