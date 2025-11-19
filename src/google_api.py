import os
import re
import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs, unquote
from itertools import product
import time
import googlemaps
from datetime import datetime
import numpy as np

_AT_RE = re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)")  # matches @lat,lng
DEFAULT_CITY = "Vienna, Austria"


markets = pd.DataFrame([
    ["MQ", "https://g.page/weihnachtsquartier?share", "14:00", "23:00"],
    ["Altes AKH", "https://goo.gl/maps/vLFEPeaSVHzfksP77", "11:00", "23:00"],
    ["Am Hof", "https://goo.gl/maps/2cMY3oeEZbqstDtP6", "10:00", "21:00"],
    ["Spittelberg", "https://goo.gl/maps/M1cs1DnR1NJRnzPy5", "10:00", "21:30"],
    ["Stephansplatz", "https://goo.gl/maps/Bg3JX4wNoKwmnpv5A", "11:00", "21:00"],
    ["Opera", "https://goo.gl/maps/zRGFceVt4vgKmicm7", "11:00", "21:00"],
    ["Türkenschanzpark", "https://goo.gl/maps/SmpWwiEbWanCXuLUA", "12:00", "22:00"],
    ["Maria-Theresien-Platz", "https://goo.gl/maps/dLFGPAZB7E5UHQNt6", "11:00", "21:00"],
    ["Blumengärten Hirschstetten", "https://goo.gl/maps/UodxLTKcLArtyG9i8", "10:00", "22:00"],
    ["Palais Liechtenstein", "https://goo.gl/maps/qnUX4zmdazoCtY3x9", "11:00", "21:00"],
    ["Belvedere", "https://g.page/belvederemuseum?share", "10:00", "21:00"],
    ["Karlsplatz", "https://goo.gl/maps/9UAJTtsxSRAmrPuU7", "12:00", "20:00"],
    ["Messe", "https://goo.gl/maps/mgUHYBriHmwAFcK19", "14:00", "22:00"],
    ["Altwiener Christkindlmarkt", "https://goo.gl/maps/QbTxRmduaxttA3Tz5", "10:00", "21:00"],
    ["Biobauern-Adventmarkt", "https://goo.gl/maps/Fc8DGKbv3aMZjVec7", "10:00", "19:30"],
    ["Rathaus", "https://goo.gl/maps/Xq7g7TsExSszrhsB6", "10:00", "21:30"],
    ["Schönbrunn", "https://goo.gl/maps/KY6oixzsxM5PVjvb8", "10:00", "21:00"],
    ["Prater / Riesenrad", "https://goo.gl/maps/bJ2obKMdq2nZWiQE6", "11:00", "22:00"],
    ["Mittelalterlicher Adventmarkt", "https://goo.gl/maps/r2EJuj1KivV2HmYj9", "09:00", "22:00"],
    ["Weihnachtsmarkt am Michaelerplatz", "https://goo.gl/maps/vyGZaJK2gnvRvje98", "10:00", "20:00"],
    ["Schloss Wilhelminenberg", "https://goo.gl/maps/LYSYyQ6LfiwkFGXq8", "11:00", "20:00"],
    ["Advent in der Stallburg", "https://goo.gl/maps/tiqojzWBSU2VVfTw9", "11:00", "20:00"],
    ["Adventmarkt Mariahilf", "https://goo.gl/maps/KhmGod5UH9k7GFYp9", "09:00", "20:00"],
    ["IKEA Westbahnhof", "https://goo.gl/maps/fV8e9wMTG611ZJTZ6", "14:00", "20:00"],
    ["Christkindlmarkt Floridsdorf (am Franz-Jonas-Platz)", "https://goo.gl/maps/cRwood7CfKZVjyCe8", "09:00", "21:00"],
    ["Adventmark Verkehrsmuseum Remise", "https://goo.gl/maps/6PJ6FzGiNYF7LQun7", "14:00", "21:00"],
    ["Weihnacht im Wald", "https://goo.gl/maps/UaQ2izUcyZzfHr1GA", "16:00", "21:00"],
    ["Adventmarkt Favoriten", "https://goo.gl/maps/5a92CE7tc1PdRnVo6", "10:00", "20:30"],
    ["Winterzauber im Böhmischen Prater", "https://goo.gl/maps/u6Smhr98B1iztBrg8", "11:00", "20:00"],
    ["Adventmarkt Meidling", "https://goo.gl/maps/pVgbJNCYryCeyaRt8", "10:00", "20:30"],
    ["Ottakringer Weihnachtszauber", "https://goo.gl/maps/X2yJEAZA8HF1c5Y86", "11:00", "22:00"],
    ["Adventmarkt im Schloss Neugebäude", "https://goo.gl/maps/SVhtiYyTX69Fnqw97", "10:00", "20:00"]
], columns=["Name", "Map", "Opens", "Closes"])

gmaps = googlemaps.Client(key="string") 


def _addresses_from_names(df: pd.DataFrame, default_city: str = DEFAULT_CITY) -> list[str]:
    """Build geocodable address strings like "Name, Vienna, Austria" for each row."""
    return [f"{name}, {default_city}" for name in df["Name"].tolist()]


def compute_pairwise_distance_matrix(
    df: pd.DataFrame,
    use_departure_now_for_driving: bool = True,
    units: str = "metric"
) -> pd.DataFrame:
    """
    Compute pairwise distance matrix for the given dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the names of the markets (column 'Name').
    use_departure_now_for_driving : bool
        Whether to use the current time as departure time for public transport requests.
    units : str, optional
        Units for distance, by default "metric".

    Returns
    -------
    pd.DataFrame
        DataFrame containing the pairwise distances for the given dataframe.
    """
    origins = _addresses_from_names(df)
    base_kwargs = {"units": units, "region": "at"}

    rows_out = []

    for i, origin in enumerate(origins):
        print("Now at:", origin, i + 1, "/", len(origins))
        for j, destination in enumerate(origins):
            # skip self-pairs
            if i == j:
                continue

            # 1) Walking request
            walk_resp = gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode="walking",
                **base_kwargs
            )
            walk_el = walk_resp["rows"][0]["elements"][0]
            if walk_el.get("status") != "OK":
                # if even walking fails, skip this pair
                continue

            walk_distance = walk_el.get("distance", {})
            walk_duration = walk_el.get("duration", {})
            walk_seconds = walk_duration.get("value")

            # 2) Public transport request
            transit_kwargs = base_kwargs.copy()
            transit_kwargs["mode"] = "transit"
            if use_departure_now_for_driving:
                transit_kwargs["departure_time"] = datetime.now()

            transit_resp = gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                **transit_kwargs
            )
            transit_el = transit_resp["rows"][0]["elements"][0]

            # default: use walking
            chosen_mode = "walking"
            chosen_distance = walk_distance
            chosen_seconds = walk_seconds

            # if transit is available, compare times
            if transit_el.get("status") == "OK":
                transit_distance = transit_el.get("distance", {})
                transit_duration = transit_el.get("duration", {})
                transit_seconds = transit_duration.get("value")

                # PT is 50% faster → PT time <= 0.5 * walking time
                if (
                    transit_seconds is not None
                    and walk_seconds is not None
                    and transit_seconds <= 0.5 * walk_seconds
                ):
                    chosen_mode = "transit"
                    chosen_distance = transit_distance
                    chosen_seconds = transit_seconds

            rows_out.append({
                "origin": df.iloc[i]["Name"],
                "destination": df.iloc[j]["Name"],
                "mode": chosen_mode,
                "distance_meters": chosen_distance.get("value"),
                "duration_seconds": chosen_seconds,
                "opens": df.iloc[j]["Opens"],
                "closes" : df.iloc[j]["Closes"]
                
            })
    return pd.DataFrame(rows_out)


def find_inbetween_way_points(df: pd.DataFrame, margin_percent: int) -> pd.DataFrame:
    """
    Remove direct connections (origin → destination) for which there exists a
    waypoint k with origin → k → destination not much worse than the direct route.

    margin_percent: percentage tolerance (e.g. 20 for 20%).
    We drop the direct edge if there is a via-path with
    duration_via <= direct_duration * (1 + margin_percent / 100).
    """
    df_copy = df.copy()

    for idx, row in df.iterrows():
        origin = row["origin"]
        destination = row["destination"]
        duration = row["duration_seconds"]

        # All legs starting at origin (origin -> mid)
        legs_from_origin = df[df["origin"] == origin]

        # All legs ending at destination (mid -> destination)
        legs_to_destination = df[df["destination"] == destination]

        # Join on the middle point: destination of first leg == origin of second leg
        legs_via = legs_from_origin.merge(
            legs_to_destination,
            left_on="destination",
            right_on="origin",
            suffixes=("_1", "_2")
        )

        if legs_via.empty:
            continue

        # Total duration via the waypoint k
        via_durations = (
            legs_via["duration_seconds_1"] + legs_via["duration_seconds_2"]
        )

        # allowed max duration via waypoint (e.g. 20% longer than direct)
        allowed = duration * (1 + margin_percent / 100.0)

        # If any via-route is "good enough", drop the direct edge
        if (via_durations <= allowed).any():
            df_copy = df_copy.drop(index=idx)

        
    df_copy['duration_walking_min'] = np.ceil(df_copy['duration_seconds'] / 60).astype(int) 
    df_copy = df_copy.drop("duration_seconds", axis=1)
        
    return df_copy


if __name__ == "__main__":
    # Build the matrix using names + city for reliable geocoding
    results_df = compute_pairwise_distance_matrix(markets)
    print(results_df.shape)
    print(results_df.head())

    # Optionally simplify graph by removing edges that can be replaced
    # by a path via another market that is at most 20% longer
    simplified_df = find_inbetween_way_points(results_df, margin_percent=20)

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
    DATA_DIR = os.path.join(BASE_DIR, "data")

    output_path = os.path.join(DATA_DIR, "datapairwise_travel_times_simplified.csv")

    simplified_df.to_csv(output_path, index=False)