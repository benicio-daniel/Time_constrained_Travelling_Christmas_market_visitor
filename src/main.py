import random
from src.classes.google_maps import GoogleMaps
from src.classes.ant import Ant
from src.classes.ant_colony import Ant_Colony
from src.classes.ant_optimizer import Ant_Optimizer

def test_1(generations: int = 2,
           ants_per_colony: int = 20,
           stay_time: int = 30,
           time_limit: str = "23:00", # cause latest market closes there
           cut_off: float = 0.5,
           seed: int = 42,
           verbose = 0) -> None:
    
    random.seed(seed)

    # ------------------------------------------------------------------
    # 1) Load Google Maps
    # ------------------------------------------------------------------
    maps = GoogleMaps()

    # All markets and opening times
    all_markets, opening_times  = maps.get_all_markets()

    # ------------------------------------------------------------------
    # 2) Initialize Optimizer therefore Colonies
    # ------------------------------------------------------------------
    optimizer = Ant_Optimizer(
        maps_service_objekt = maps,
        num_colonies        = len(all_markets),
        ants_per_colony     = ants_per_colony,
        stay_time           = stay_time,
        time_limit          = time_limit,
        mutation            = 1,     # only exploration
        verbose             = verbose
    )
    optimizer.initialize_colonies(all_markets, opening_times)

    # ------------------------------------------------------------------
    # 3) Run Simulation
    # ------------------------------------------------------------------
    for gen in range(1, generations):
        paths = optimizer.run_one_generation()# gives paths for each colony
        
        print(f"Generation {gen} finished.")

        # ------------------------------------------------------------------
        # 4) Print Results (best cut-off% starting markets by there score)
        # ------------------------------------------------------------------
    
        results = []

        for colony in optimizer.colonies:
            visited_counts = [len(ant.visited) for ant in colony.ants]
            avg_visited = sum(visited_counts) / len(visited_counts)
            results.append((colony.start_market, avg_visited))

        # Sort descending (best → worst)
        results.sort(key=lambda x: x[1], reverse=True)

        # Determine how many markets to return
        cutoff_count = max(1, int(len(results) * cut_off))
        top_markets = results[:cutoff_count]

        print("\n=== Colony Ranking by Avg Visited Markets ===")
        print(f"Top {cut_off*100:.0f}% ({cutoff_count} von {len(results)} Startlocations)\n")

        for market, avg_score in top_markets:
            print(f"- {market:25s}  Ø visited: {avg_score:.2f}")

        # Only print market names (if that’s what you want)
        print("\nTop Markets (Names Only):")
        print([m for m, _ in top_markets])
        optimizer.advance_to_next_generation()
        
if __name__ == "__main__":
    test_1(generations=2)
