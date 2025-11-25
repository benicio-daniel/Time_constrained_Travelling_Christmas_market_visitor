import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

# 1. Load your CSV (same folder as this file)
df = pd.read_csv("data/datapairwise_travel_times_simplified.csv")

# (Optional) filter edges, e.g. only walking connections
# df = df[df["mode"] == "walking"]

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
plt.show()