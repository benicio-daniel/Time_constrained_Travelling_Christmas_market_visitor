import typing
import pandas as pd
class GoogleMaps:
    def __init__(self) -> None:
        self.df = pd.read_csv("data/pairwise_travel_times.csv")
    def get_destinations(self, origin: str) -> dict[str, tuple[int, float]]:
        """
        Returns a dictionary of destinations for a given origin.
    
        Args:
            origin (str): The origin of the route.
    
        Returns:
            dict[str, tuple[int, float]]: Keys are destinations, values are
            (duration_seconds, pheromone).
        """
        subset = self.df.loc[
            self.df["origin"] == origin, 
            ["destination", "duration_seconds", "pheromone"]
        ]
    
        # Convert to dictionary: destination → (duration, pheromone)
        destinations = {
            row["destination"]: (int(row["duration_seconds"]), float(row["pheromone"]))
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
    
    def get_open_and_close_times(self) -> tuple[dict[str, int], dict[str, int]]:
        """
        Returns two dictionaries: opening times and closing times for each market.

        Returns:
            tuple[dict[str, int], dict[str, int]]: 
                - First dictionary maps market to opening time.
                - Second dictionary maps market to closing time.
        """
        pass
        
if __name__ == "__main__":

    GM = GoogleMaps()
    print(GM.get_destinations("MQ"))