import pandas as pd
from datetime import time
from datetime import timedelta
from pathlib import Path

class GoogleMaps:
    def __init__(self, pheromone_decay_factor:float = 0.9, pheromone_constant:float = 1) -> None:
        """
        Initialises the GoogleMaps object by reading the pairwise travel times from a csv file.

        The csv file should be located in the 'data' directory and should contain columns 'origin', 'destination', 'opens', 'closes' and 'duration_walking_min'.

        The 'opens' and 'closes' columns should be in the format 'HH:MM' and will be converted to datetime.time objects.

        The 'duration_walking_min' column should contain the duration of travel in minutes between each origin and destination.

        The data will be stored in a pandas DataFrame object which can be accessed through the 'df' attribute.

        """
        
        # haven't found a better way to do this
        CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "datapairwise_travel_times_simplified.csv"

        self.df = pd.read_csv(CSV_PATH)
        self.df["opens"] = pd.to_datetime(self.df["opens"], format="%H:%M").dt.time
        self.df["closes"] = pd.to_datetime(self.df["closes"], format="%H:%M").dt.time
        def to_minutes(t):
            return t.hour * 60 + t.minute
        self.df["opens_min"] = self.df["opens"].apply(to_minutes)
        self.df["closes_min"] = self.df["closes"].apply(to_minutes)

        self.df["pheromone"] = 1
        assert 0 <= pheromone_decay_factor <=1
        self.decay_factor = pheromone_decay_factor
        self.pheromone_constant = pheromone_constant
        self.max_pheromone = 100
    
    def get_destinations(self, origin: str) -> dict[str, tuple[int, float, time, time]]:
        """
        Returns a dictionary containing the destinations and their respective travel times, pheromone values, opening and closing times for a given origin.

        Args:
            origin (str): The origin to get the destinations for.

        Returns:
            dict[str, tuple[int, float, time, time]]: A dictionary containing the destinations as keys and tuples containing the duration, pheromone, opening and closing times as values.
        """
        subset = self.df.loc[
            self.df["origin"] == origin, 
            ["destination", "duration_walking_min", "pheromone", "opens_min", "closes_min"]
        ]
    
        # Convert to dictionary: destination → (duration, pheromone, opens, closes)
        destinations = {
            row["destination"]: (
                int(row["duration_walking_min"]),
                float(row["pheromone"]),
                int(row["opens_min"]),
                int(row["closes_min"]),
            )
            for _, row in subset.iterrows()
        }

        return destinations
    
    def update_pheromones(self, paths: list[tuple[list[tuple[str, str]], float]]):
        """
        Update pheromones based on a list of (path, cost) tuples.

        Args:
            paths: List of tuples (edges, cost)
                   edges = [(origin, destination), ...]
                   cost = numeric path cost (lower is better)
        """
        # 1) Evaporation
        self.df["pheromone"] *= self.decay_factor

        # 2) Deposit
        for edges, cost in paths:
            deposit = self.pheromone_constant / cost  # Q / L_k
            for (origin, destination) in edges:
                self.df.loc[
                    (self.df["origin"] == origin) &
                    (self.df["destination"] == destination),
                    "pheromone"
                ] += deposit
        self.df["pheromone"] = self.df["pheromone"].clip(lower=1, upper=self.max_pheromone)

    def get_all_markets(self, visited_markets:list[str]|None = None) -> tuple[list[str], list[time]]:
        """
        Returns two lists:
        - A list of all markets (strings)
        - A list of the corresponding opening times for each market in the same order as the markets list as time objects
        """

        grouped = self.df.groupby("destination")["opens"].first()
        if visited_markets is not None:
            grouped = grouped[~grouped.index.isin(visited_markets)]
        all_markets = grouped.index.tolist()
        opening_times = grouped.tolist()
        return all_markets, opening_times