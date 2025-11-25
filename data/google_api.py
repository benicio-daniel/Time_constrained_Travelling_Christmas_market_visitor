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
import networkx as nx
import matplotlib.pyplot as plt


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
    ["Bio-Markt Freyung", "https://goo.gl/maps/Fc8DGKbv3aMZjVec7", "10:00", "19:30"],
    ["Rathaus", "https://goo.gl/maps/Xq7g7TsExSszrhsB6", "10:00", "21:30"],
    ["Schönbrunn", "https://goo.gl/maps/KY6oixzsxM5PVjvb8", "10:00", "21:00"],
    ["Prater / Riesenrad", "https://goo.gl/maps/bJ2obKMdq2nZWiQE6", "11:00", "22:00"],
    ["Heeresgeschichtliches Museum", "https://goo.gl/maps/r2EJuj1KivV2HmYj9", "09:00", "22:00"],
    ["Weihnachtsmarkt am Michaelerplatz", "https://goo.gl/maps/vyGZaJK2gnvRvje98", "10:00", "20:00"],
    ["Schloss Wilhelminenberg", "https://goo.gl/maps/LYSYyQ6LfiwkFGXq8", "11:00", "20:00"],
    ["Advent in der Stallburg", "https://goo.gl/maps/tiqojzWBSU2VVfTw9", "11:00", "20:00"],
    ["Adventmarkt Mariahilf", "https://goo.gl/maps/KhmGod5UH9k7GFYp9", "09:00", "20:00"],
    ["IKEA Westbahnhof", "https://goo.gl/maps/fV8e9wMTG611ZJTZ6", "14:00", "20:00"],
    ["Christkindlmarkt Floridsdorf (am Franz-Jonas-Platz)", "https://goo.gl/maps/cRwood7CfKZVjyCe8", "09:00", "21:00"],
    ["Adventmark Verkehrsmuseum Remise", "https://goo.gl/maps/6PJ6FzGiNYF7LQun7", "14:00", "21:00"],
    ["Weihnacht im Wald", "https://goo.gl/maps/UaQ2izUcyZzfHr1GA", "16:00", "21:00"],
    ["Favoritenstraße 83-77", "https://goo.gl/maps/5a92CE7tc1PdRnVo6", "10:00", "20:30"],
    ["Böhmischer Prater", "https://goo.gl/maps/u6Smhr98B1iztBrg8", "11:00", "20:00"],
    ["Meidlinger Platzl", "https://goo.gl/maps/pVgbJNCYryCeyaRt8", "10:00", "20:30"],
    ["Ottakringer Weihnachtszauber", "https://goo.gl/maps/X2yJEAZA8HF1c5Y86", "11:00", "22:00"],
    ["Adventmarkt im Schloss Neugebäude", "https://goo.gl/maps/SVhtiYyTX69Fnqw97", "10:00", "20:00"]
], columns=["Name", "Map", "Opens", "Closes"])

gmaps = googlemaps.Client(key="AIzaSyA714W9zEFlvRrnTqYGpMFhLShCeGPprwg") 


def _addresses_from_names(df: pd.DataFrame, default_city: str = DEFAULT_CITY) -> list[str]:
    """Build geocodable address strings like "Name, Vienna, Austria" for each row."""
    return [f"{name}, {default_city}" for name in df["Name"].tolist()]


def compute_walking_distance_matrix(
    df: pd.DataFrame,
    units: str = "metric"
) -> pd.DataFrame:
    """
    Compute pairwise walking distance matrix for the given dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the names of the markets (column 'Name').
    units : str, optional
        Units for distance, by default "metric".

    Returns
    -------
    pd.DataFrame
        DataFrame containing the pairwise walking distances for the given dataframe.
    """
    origins = _addresses_from_names(df)
    base_kwargs = {"units": units, "region": "at"}

    rows_out: list[dict] = []

    for i, origin in enumerate(origins):
        print("Now at:", origin, i + 1, "/", len(origins))
        for j, destination in enumerate(origins):
            # skip self-pairs
            if i == j:
                continue

            # Walking request only
            walk_resp = gmaps.distance_matrix(  # type: ignore
                origins=[origin],
                destinations=[destination],
                mode="walking",
                **base_kwargs,
            )
            walk_el = walk_resp["rows"][0]["elements"][0]
            if walk_el.get("status") != "OK":
                # if walking fails, skip this pair
                continue

            walk_distance = walk_el.get("distance", {})
            walk_duration = walk_el.get("duration", {})
            walk_seconds = walk_duration.get("value")

            rows_out.append({
                "origin": df.iloc[i]["Name"],
                "destination": df.iloc[j]["Name"],
                "mode": "walking",
                "distance_meters": walk_distance.get("value"),
                "duration_seconds": walk_seconds,
                "opens": df.iloc[j]["Opens"],
                "closes": df.iloc[j]["Closes"],
            })

    return pd.DataFrame(rows_out)


def apply_public_transport(
    df_edges: pd.DataFrame,
    markets_df: pd.DataFrame,
    use_departure_now_for_driving: bool = True,
    units: str = "metric",
    faster_factor: float = 0.5,
) -> pd.DataFrame:
    """\
    For each existing edge in df_edges (assumed to be walking-only),
    check whether public transport is sufficiently faster.

    If so, overwrite mode, distance_meters and duration_seconds with the
    transit values.

    Parameters
    ----------
    df_edges : pd.DataFrame
        Edge list with at least origin, destination, duration_seconds, distance_meters, mode.
    markets_df : pd.DataFrame
        DataFrame with column 'Name' used to build geocodable addresses.
    use_departure_now_for_driving : bool
        Whether to use the current time as departure_time for transit requests.
    units : str
        Units for the Google Maps Distance Matrix API.
    faster_factor : float
        Public transport is considered better if
        transit_seconds <= faster_factor * walking_seconds.
    """
    df_result = df_edges.copy()

    # Map market names to addresses
    addresses = _addresses_from_names(markets_df)
    name_to_addr = {
        markets_df.iloc[i]["Name"]: addresses[i] for i in range(len(markets_df))
    }

    base_kwargs = {"units": units, "region": "at"}
    if use_departure_now_for_driving:
        base_kwargs["departure_time"] = datetime.now()  # type: ignore

    for idx, row in df_result.iterrows():
        origin_name = row["origin"]
        dest_name = row["destination"]

        origin_addr = name_to_addr.get(origin_name)
        dest_addr = name_to_addr.get(dest_name)

        if origin_addr is None or dest_addr is None:
            continue

        walk_seconds = row.get("duration_seconds")
        if walk_seconds is None:
            continue

        try:
            transit_resp = gmaps.distance_matrix(  # type: ignore
                origins=[origin_addr],
                destinations=[dest_addr],
                mode="transit",
                **base_kwargs,
            )
        except Exception:
            # In case of transient API errors, skip this edge
            continue

        transit_el = transit_resp["rows"][0]["elements"][0]
        if transit_el.get("status") != "OK":
            continue

        transit_distance = transit_el.get("distance", {})
        transit_duration = transit_el.get("duration", {})
        transit_seconds = transit_duration.get("value")

        if transit_seconds is None:
            continue

        # If transit is sufficiently faster, update this edge
        if transit_seconds <= faster_factor * walk_seconds:
            df_result.at[idx, "mode"] = "transit"
            df_result.at[idx, "distance_meters"] = transit_distance.get("value")
            df_result.at[idx, "duration_seconds"] = transit_seconds

    return df_result


def find_inbetween_way_points(df: pd.DataFrame, margin_percent: int) -> pd.DataFrame:
    """
    Remove direct connections (origin → destination) for which there exists a
    waypoint k with origin → k → destination not much worse than the direct route.

    margin_percent: percentage tolerance (e.g. 20 for 20%).
    We drop the direct edge if there is a via-path with
    duration_via <= direct_duration * (1 + margin_percent / 100).

    Additionally: for each origin, we always keep at least the two shortest
    connections (by distance_meters), even if they would be removable.
    """
    df_copy = df.copy()

    for idx, row in df.iterrows():
        origin = row["origin"]
        destination = row["destination"]
        duration = row["distance_meters"]

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
            legs_via["distance_meters_1"] + legs_via["distance_meters_2"]
        )

        # allowed max duration via waypoint (e.g. 20% longer than direct)
        allowed = duration * (1 + margin_percent / 100.0)

        # If no via-route is "good enough", keep this edge
        if not (via_durations <= allowed).any():
            continue

        # --- NEW PART: ensure at least two shortest edges per origin remain ---

        # Current edges for this origin in the *pruned* df_copy
        origin_edges_current = df_copy[df_copy["origin"] == origin]

        # If we already have <= 2 edges left from this origin, we don't drop any more
        if len(origin_edges_current) <= 2:
            continue

        # Identify the two shortest edges (by distance) from this origin
        two_shortest = origin_edges_current.nsmallest(2, "distance_meters")

        # If this edge is among the two shortest, keep it
        if idx in two_shortest.index:
            continue

        # Otherwise it's safe to drop
        df_copy = df_copy.drop(index=idx)

    return df_copy


def make_graph(df):

    # 2. Build a directed graph from the edge list
    G = nx.from_pandas_edgelist(
        df,
        source="origin",
        target="destination",
        edge_attr=True,
        create_using=nx.DiGraph()
    )

    # 3. Layout and plot
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=800,
        font_size=8,
        arrows=True
    )

    # Save plot to /plots folder
    os.makedirs("plots", exist_ok=True)
    plt.savefig("plots/graph_connections.png", dpi=300, bbox_inches="tight")

    plt.tight_layout()

    

if __name__ == "__main__":
    # 1) Build the matrix using names + city for reliable geocoding (walking only)
    walking_df = compute_walking_distance_matrix(markets)
    print("Walking matrix shape:", walking_df.shape)

    # 2) Simplify graph by removing edges that can be replaced
    #    by a path via another market that is at most 20% longer
    simplified_df = find_inbetween_way_points(walking_df, margin_percent=10)
    print("Simplified matrix shape:", simplified_df.shape)

    # 3) Enrich remaining edges with public transport where it is
    #    significantly faster than walking
    final_df = apply_public_transport(simplified_df, markets)

    # Optional: add a duration in whole minutes for convenience
    final_df["duration_min"] = np.ceil(final_df["duration_seconds"] / 60).astype(int)
    final_df.drop(columns=["duration_seconds"], inplace=True)
    
    #save to csv
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # project root
    DATA_DIR = os.path.join(BASE_DIR, "data")

    output_path = os.path.join(DATA_DIR, "datapairwise_travel_times_simplified.csv")
    make_graph(final_df)
    final_df.to_csv(output_path, index=False)