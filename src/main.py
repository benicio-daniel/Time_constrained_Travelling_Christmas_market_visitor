import random
import matplotlib.pyplot as plt
import os
from src.classes.google_maps import GoogleMaps
from src.classes.ant import Ant
from src.classes.ant_colony import Ant_Colony
from src.classes.ant_optimizer import Ant_Optimizer
import os

def cull_colonies(ant_optimizer:Ant_Optimizer,top_colonies:list[Ant_Colony], cut_off:float):
    for colonies in ant_optimizer.colonies:
        if colonies.start_market not in top_colonies:
            colonies.remove(colonies)
        

def test_1(mutation: int,
           generations: int = 2,
           ants_per_colony: int = 20,
           stay_time: int = 30,
           time_limit: str = "23:00", # cause latest market closes there
           cut_off: float = 0.5,
           seed: int = 42,
           verbose_ants: int = 0,
           verbose = 0,
           time_to_cull: int | None = None,
           set_multiple_days: bool = False,
           time_to_set_mult_days: int | None = None) -> None:
    
    """
    Runs a simulation of the Ant Colony Optimization algorithm on the given parameters.

    Parameters:
    mutation (int): The mutation type of the ants.
    generations (int, optional): The number of generations to simulate. Defaults to 2.
    ants_per_colony (int, optional): The number of ants per colony. Defaults to 20.
    stay_time (int, optional): The time the ants spend at each market. Defaults to 30.
    time_limit (str, optional): The overall time limit for the ants. Defaults to "23:00".
    cut_off (float, optional): The percentage of top markets to keep after culling. Defaults to 0.5.
    seed (int, optional): The random seed to use. Defaults to 42.
    verbose_ants (int, optional): The verbosity of the ants. Defaults to 0. 1 is optimizer, 2 is colony, 3 is ants
    verbose (int, optional): The verbosity of the simulation. Defaults to 0. 1 prints fitness, 2 prints evaluation table every generation
    time_to_cull (int | None, optional): The generation after which to cull the worst-performing colonies. Defaults to None.
    set_multiple_days (bool, optional): Whether the ants can visit markets multiple times in a single day. Defaults to False.

    Returns:
    None
    """
    random.seed(seed)
    print("Starting Test 1")
    # ------------------------------------------------------------------
    # 1) Load Google Maps
    # ------------------------------------------------------------------
    maps = GoogleMaps()

    # All markets and opening times
    all_markets, opening_times  = maps.get_all_markets()
    # Establish history logging
    gen_avg_fitness = []
    gen_max_fitness = []
    avg_visited_history = {market: [] for market in all_markets}
    max_visited_history = {market: [] for market in all_markets}

    # ------------------------------------------------------------------
    # 2) Initialize Optimizer therefore Colonies
    # ------------------------------------------------------------------
    optimizer = Ant_Optimizer(
        maps_service_objekt = maps,
        num_colonies        = len(all_markets),
        ants_per_colony     = ants_per_colony,
        stay_time           = stay_time,
        time_limit          = time_limit,
        mutation            = mutation,
        ants_multiple_days  = set_multiple_days,
        verbose             = verbose_ants
    )
    optimizer.initialize_colonies(all_markets, opening_times)

       # ------------------------------------------------------------------
    # 3) Run Simulation
    # ------------------------------------------------------------------
    print("Running Simulation...")
    for gen in range(1, generations + 1):
        if gen == time_to_set_mult_days and set_multiple_days:
            optimizer.set_ants_multiple_days()

        paths = optimizer.run_one_generation()  # gives paths for each colony
        print(f"Generation {gen} finished.")

        # ------------------------------------------------------------------
        # 4) Evaluate Results, either print or cull
        # ------------------------------------------------------------------
        # fitness across all ants / colonies
        fitness_values = [fitness for (_, fitness) in paths]
        avg_f = sum(fitness_values) / len(fitness_values)
        max_f = max(fitness_values)

        gen_avg_fitness.append(avg_f)
        gen_max_fitness.append(max_f)

        # per-colony visited stats
        results = []
        for colony in optimizer.colonies:
            visited_counts = [len(ant.visited) for ant in colony.ants]
            avg_visited = sum(visited_counts) / len(visited_counts)
            max_visited = max(visited_counts)
            results.append((colony.start_market, avg_visited))

            # log per-start-market stats
            avg_visited_history[colony.start_market].append(avg_visited)
            max_visited_history[colony.start_market].append(max_visited)

        # Sort descending (best → worst)
        results.sort(key=lambda x: x[1], reverse=True)

        # Determine how many markets to return
        cutoff_count = max(1, int(len(results) * cut_off))
        top_markets = results[:cutoff_count]

        if gen == time_to_cull and time_to_cull is not None:
            cull_colonies(optimizer, top_markets, cut_off)

        if gen == generations or verbose == 2:
            print("\n=== Colony Ranking by Avg Visited Markets ===")
            print(f"Top {cut_off * 100:.0f}% ({cutoff_count} von {len(results)} Startlocations)\n")

            for market, avg_score in top_markets:
                print(f"- {market:25s}  Ø visited: {avg_score:.2f}")

            print("\nTop Markets (Names Only):")
            print([m for m, _ in top_markets])

        # Always advance if not the last generation
        if gen != generations:
            optimizer.advance_to_next_generation()

    # ------------------------------------------------------------------
    # 5) Plot fitness development over generations
    # ------------------------------------------------------------------
    generations_range = range(1, generations + 1)

    plt.figure()
    plt.plot(generations_range, gen_avg_fitness, marker='o', label='Average fitness')
    plt.plot(generations_range, gen_max_fitness, marker='o', label='Max fitness')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title(f'Fitness over Generations (mutation {mutation})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # Save plot to ../data
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "..", "plots")
    os.makedirs(data_dir, exist_ok=True)
    plot_path = os.path.join(
        data_dir,
        f"fitness_over_generations_mut{mutation}_gen{generations}.png"
    )
    plt.savefig(plot_path)
    print(f"Saved fitness plot to: {plot_path}")
    plt.show()
    # ------------------------------------------------------------------
    # 6) Plot avg visited per starting market over generations
    # ------------------------------------------------------------------
    plt.figure()
    for market, series in avg_visited_history.items():
        if series:  # only plot markets that have data
            gens = range(1, len(series) + 1)
            plt.plot(gens, series, marker='o', label=market)
    plt.xlabel('Generation')
    plt.ylabel('Average visited markets')
    plt.title(f'Average visited per starting market (mutation {mutation})')
    plt.legend(fontsize='small')
    plt.grid(True)
    plt.tight_layout()
    avg_plot_path = os.path.join(
        data_dir,
        f"avg_visited_per_market_mut{mutation}_gen{generations}.png"
    )
    plt.savefig(avg_plot_path)
    print(f"Saved avg visited plot to: {avg_plot_path}")
    plt.show()
    
    # ------------------------------------------------------------------
    # 7) Plot max visited per starting market over generations
    # ------------------------------------------------------------------
    plt.figure()
    for market, series in max_visited_history.items():
        if series:  # only plot markets that have data
            gens = range(1, len(series) + 1)
            plt.plot(gens, series, marker='o', label=market)
    plt.xlabel('Generation')
    plt.ylabel('Max visited markets')
    plt.title(f'Max visited per starting market (mutation {mutation})')
    plt.legend(fontsize='small')
    plt.grid(True)
    plt.tight_layout()
    max_plot_path = os.path.join(
        data_dir,
        f"max_visited_per_market_mut{mutation}_gen{generations}.png"
    )
    plt.savefig(max_plot_path)
    print(f"Saved max visited plot to: {max_plot_path}")
    plt.show()


if __name__ == "__main__":
    test_1(mutation=2, generations=50, verbose = 0)
