import typing
import pandas as pd
from datetime import time
class GoogleMaps:
    def __init__(self) -> None:
        """
        Initialises the GoogleMaps object by reading the pairwise travel times from a csv file.

        The csv file should be located in the 'data' directory and should contain columns 'origin', 'destination', 'opens', 'closes' and 'duration_seconds'.

        The 'opens' and 'closes' columns should be in the format 'HH:MM' and will be converted to datetime.time objects.

        The 'duration_seconds' column should contain the duration of travel in seconds between each origin and destination.

        The data will be stored in a pandas DataFrame object which can be accessed through the 'df' attribute.

        """
        self.df = pd.read_csv("data/pairwise_travel_times.csv")
        self.df["opens"] = pd.to_datetime(self.df["opens"], format="%H:%M").dt.time
        self.df["closes"] = pd.to_datetime(self.df["closes"], format="%H:%M").dt.time
        
        
        
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
            ["destination", "duration_seconds", "pheromone"]
        ]
    
        # Convert to dictionary: destination → (duration, pheromone)
        destinations = {
            row["destination"]: (int(row["duration_seconds"]), float(row["pheromone"]), row["opens"], row["closes"])
            for _, row in subset.iterrows()
        }
    
        return destinations
    def change_pheromones(self, origin: str, destination: str, pheromone: float):
        """
        Changes the pheromone of a given route in the dataframe.

        Args:
            origin (str): The origin of the route.
            destination (str): The destination of the route.
            pheromone (float): The new pheromone value.

        """
        self.df.loc[(self.df["origin"] == origin) & (self.df["destination"] == destination), "pheromone"] = pheromone
        
#if __name__ == "__main__":
#    pass