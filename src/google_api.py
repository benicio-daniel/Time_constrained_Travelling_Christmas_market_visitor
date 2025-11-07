import os
import re
import pandas as pd
import requests
from urllib.parse import urlparse, parse_qs, unquote
from itertools import product
import time
import googlemaps
from datetime import datetime

API_KEY = "AIzaSyDGJMwIPIcqXJl8cFlgH8Vc-dnbXfCS-Xc"  # put your key in env
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

gmaps = googlemaps.Client(key = "AIzaSyB-fDj2Jxzlr20Re3VjVRX0_50XeaxecDk")

def _addresses_from_names(df: pd.DataFrame, default_city: str = DEFAULT_CITY) -> list[str]:
    """Build geocodable address strings like "Name, Vienna, Austria" for each row."""
    return [f"{name}, {default_city}" for name in df["Name"].tolist()]

def compute_pairwise_distance_matrix(df: pd.DataFrame,
                                     mode: str = "walking",
                                     use_departure_now_for_driving: bool = True,
                                     units: str = "metric") -> pd.DataFrame:
    origins = _addresses_from_names(df)
    kwargs = {"mode": mode, "units": units, "region": "at"}

    rows_out = []

    for i, origin in enumerate(origins):
        for j, destination in enumerate(origins):
            if i == j:
                continue
            try:
                resp = gmaps.distance_matrix(origins=[origin], destinations=[destination], **kwargs)
                el = resp["rows"][0]["elements"][0]
                print("Now at:",i)
                if el.get("status") != "OK":
                    continue
                distance = el.get("distance", {})
                duration = el.get("duration", {})
                duration_in_traffic = el.get("duration_in_traffic")
                rows_out.append({
                    "origin": df.iloc[i]["Name"],
                    "destination": df.iloc[j]["Name"],
                    "mode": mode,
                    "distance_meters": distance.get("value"),
                    "distance_text": distance.get("text"),
                    "duration_seconds": duration.get("value"),
                    "duration_text": duration.get("text"),
                    "duration_in_traffic_seconds": (duration_in_traffic or {}).get("value") if duration_in_traffic else None,
                    "duration_in_traffic_text": (duration_in_traffic or {}).get("text") if duration_in_traffic else None,
                })
            except Exception:
                continue

    return pd.DataFrame(rows_out)

if __name__ == "__main__":
    # Build the matrix using names + city for reliable geocoding
    results_df = compute_pairwise_distance_matrix(markets, mode="walking")
    print(results_df.shape)
    print(results_df.head())
    results_df.to_csv("pairwise_travel_times.csv", index=False)