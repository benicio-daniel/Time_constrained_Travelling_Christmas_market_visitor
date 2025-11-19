import random
from google_maps import GoogleMaps
from ant import Ant
from ant_colony import Ant_Colony
from ant_optimizer import Ant_Optimizer

def test_1(generations: int = 1,
           ants_per_colony: int = 10,
           stay_time: int = 30,
           time_limit: int = 2300,
           seed: int = 42) -> None:
    
    random.seed(seed)

    # ------------------------------------------------------------------
    # 1) Load Google Maps
    # ------------------------------------------------------------------
    maps = GoogleMaps()

    # All markets and opening times
    grouped       = maps.df
    all_markets   = grouped["origin"].tolist()
    opening_times = grouped["opens"].tolist()

    # ------------------------------------------------------------------
    # 2) Initialize Optimizer therefore Colonies
    # ------------------------------------------------------------------
    optimizer = Ant_Optimizer(
        maps_service_objekt = maps,
        num_colonies        = len(all_markets),
        ants_per_colony     = ants_per_colony,
        stay_time           = stay_time,
        time_limit          = time_limit,
        mutation            = 1     # only exploration
    )
    optimizer.initialize_colonies(all_markets, opening_times)

    # ------------------------------------------------------------------
    # 3) Run Simulation (may not be format of path returns)
    # ------------------------------------------------------------------
    for gen in range(1, generations + 1):
        paths = optimizer.run_one_generation()   # gives paths for each colony
        print(f"Generation {gen} abgeschlossen – {len(paths)} Colonies bewegt")

    # ------------------------------------------------------------------
    # 4) Print Results
    # ------------------------------------------------------------------
    print("\n=== Colony-Overview ===")
    for idx, colony in enumerate(optimizer.colonies, 1):
        # returns max score for each colony
        best_score = max(score for _, score in paths[idx-1])
        print(f"Colony {idx:2}: Start {colony.start_market:25}  Best-Fitness {best_score}")
        

if __name__ == "__main__":
    test_1()
